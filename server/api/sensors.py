from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any

from fastapi import APIRouter, status

from display.display import create_display
from display.renderer import PlantPanelData, render_plant_dashboard
from models.api.sensor_reading import SensorReading


router = APIRouter(tags=["Sensors"])
_display_lock = Lock()
_state_lock = Lock()


@dataclass(frozen=True)
class PlantThresholds:
    moisture_low: float
    moisture_high: float
    temperature_low_f: float
    temperature_high_f: float
    humidity_low: float
    humidity_high: float
    light_low_lux: float
    light_high_lux: float

    @classmethod
    def from_environment(cls) -> "PlantThresholds":
        return cls(
            moisture_low=_env_float("PLANT_MOISTURE_LOW_PERCENT", 30.0),
            moisture_high=_env_float("PLANT_MOISTURE_HIGH_PERCENT", 80.0),
            temperature_low_f=_env_float("PLANT_TEMPERATURE_LOW_F", 55.0),
            temperature_high_f=_env_float("PLANT_TEMPERATURE_HIGH_F", 90.0),
            humidity_low=_env_float("PLANT_HUMIDITY_LOW_PERCENT", 30.0),
            humidity_high=_env_float("PLANT_HUMIDITY_HIGH_PERCENT", 80.0),
            light_low_lux=_env_float("PLANT_LIGHT_LOW_LUX", 100.0),
            light_high_lux=_env_float("PLANT_LIGHT_HIGH_LUX", 10_000.0),
        )


@dataclass(frozen=True)
class PlantDisplayState:
    plant_name: str
    state: str
    health_percent: int


_latest_plants: dict[str, PlantDisplayState] = {}
_last_render_signature: tuple[tuple[str, str, int], ...] | None = None


def _env_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        return float(raw_value)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable {name} must be numeric; "
            f"received {raw_value!r}."
        ) from exc


def _env_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable {name} must be an integer; "
            f"received {raw_value!r}."
        ) from exc


def _within_score(value: float, low: float, high: float) -> float:
    """Return a 0-100 score based on distance from an acceptable range."""
    if low <= value <= high:
        return 100.0

    range_width = max(1.0, high - low)
    distance = low - value if value < low else value - high
    return max(0.0, 100.0 - (distance / range_width) * 100.0)


def _determine_state(
    reading: SensorReading,
    thresholds: PlantThresholds,
) -> str:
    """Return one asset name from assets/characters/<state>.png."""
    moisture = reading.moisture_1_percent

    # Priority order: conditions that can damage the plant most quickly first.
    if moisture <= thresholds.moisture_low:
        return "needs_water"
    if moisture >= thresholds.moisture_high:
        return "too_wet"
    if reading.temperature_f >= thresholds.temperature_high_f:
        return "too_hot"
    if reading.temperature_f <= thresholds.temperature_low_f:
        return "too_cold"
    if reading.light_lux <= thresholds.light_low_lux:
        return "low_light"
    if reading.light_lux >= thresholds.light_high_lux:
        return "too_hot"

    return "healthy"


def _calculate_health(
    reading: SensorReading,
    thresholds: PlantThresholds,
) -> int:
    moisture_score = _within_score(
        reading.moisture_1_percent,
        thresholds.moisture_low,
        thresholds.moisture_high,
    )
    temperature_score = _within_score(
        reading.temperature_f,
        thresholds.temperature_low_f,
        thresholds.temperature_high_f,
    )
    humidity_score = _within_score(
        reading.humidity_percent,
        thresholds.humidity_low,
        thresholds.humidity_high,
    )
    light_score = _within_score(
        reading.light_lux,
        thresholds.light_low_lux,
        thresholds.light_high_lux,
    )

    # Moisture has the largest influence for the initial prototype.
    weighted_score = (
        moisture_score * 0.50
        + temperature_score * 0.20
        + humidity_score * 0.15
        + light_score * 0.15
    )

    return max(0, min(100, round(weighted_score)))


def _render_signature(
    plants: list[PlantDisplayState],
) -> tuple[tuple[str, str, int], ...]:
    return tuple(
        (plant.plant_name, plant.state, plant.health_percent)
        for plant in plants
    )


@router.post(
    "/api/v1/readings",
    status_code=status.HTTP_201_CREATED,
)
def receive_sensor_reading(
    reading: SensorReading,
) -> dict[str, Any]:
    """Receive one sensor reading from a Seeed device."""
    received_at = datetime.now(timezone.utc)

    # Thresholds are read from environment variables for every request for now.
    # Later, move these values into each plant's persisted configuration.
    thresholds = PlantThresholds.from_environment()
    max_plants = max(1, _env_int("DISPLAY_MAX_PLANTS", 4))

    display_updated = process_sensor_data(
        reading=reading,
        received_at=received_at,
        thresholds=thresholds,
        max_plants=max_plants,
    )

    return {
        "accepted": True,
        "device_id": reading.device_id,
        "reading_number": reading.reading_number,
        "received_at": received_at.isoformat(),
        "display_updated": display_updated,
    }


def process_sensor_data(
    reading: SensorReading,
    received_at: datetime,
    thresholds: PlantThresholds,
    max_plants: int,
) -> bool:
    """Update the dashboard only when state or health percentage changes."""
    del received_at
    global _last_render_signature

    plant_name = os.getenv(
        f"PLANT_NAME_{reading.device_id.upper().replace('-', '_')}",
        reading.device_id,
    )

    current = PlantDisplayState(
        plant_name=plant_name,
        state=_determine_state(reading, thresholds),
        health_percent=_calculate_health(reading, thresholds),
    )

    with _state_lock:
        _latest_plants[reading.device_id] = current

        plants = list(_latest_plants.values())
        plants.sort(key=lambda plant: plant.plant_name.lower())
        plants = plants[:max_plants]

        signature = _render_signature(plants)
        if signature == _last_render_signature:
            return False

        _last_render_signature = signature

    image = render_plant_dashboard(
        plants=[
            PlantPanelData(
                plant_name=plant.plant_name,
                state=plant.state,
                health_percent=plant.health_percent,
            )
            for plant in plants
        ],
        max_plants=max_plants,
    )

    with _display_lock:
        display = create_display()
        try:
            display.initialize()
            display.show(image)
        except Exception as exc:
            print(f"Display update failed: {exc}")
            return False
        finally:
            try:
                display.shutdown()
            except Exception as exc:
                print(f"Display cleanup failed: {exc}")

    return True
