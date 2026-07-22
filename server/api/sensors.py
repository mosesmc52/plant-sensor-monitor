from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, status

from models.api.sensor_reading import SensorReading


router = APIRouter(tags=["Health"])


@router.post(
    "/api/v1/readings",
    status_code=status.HTTP_201_CREATED,
)
def receive_sensor_reading(
    reading: SensorReading,
) -> dict[str, Any]:
    """
    Receive one sensor reading from a Seeed device.
    """

    received_at = datetime.now(timezone.utc)

    print("--------------------------------")
    print("Sensor reading received")
    print(f"Device: {reading.device_id}")
    print(f"Reading number: {reading.reading_number}")
    print(f"Temperature: {reading.temperature_f:.1f} F")
    print(f"Humidity: {reading.humidity_percent:.1f}%")
    print(f"Light: {reading.light_lux:.1f} lux")
    print(f"Moisture 1: {reading.moisture_1_percent}%")
    print(f"Moisture 2: {reading.moisture_2_percent}%")
    print(f"Device uptime: {reading.uptime_seconds} seconds")
    print(f"Received at: {received_at.isoformat()}")

    process_sensor_data(
        reading=reading,
        received_at=received_at,
    )

    return {
        "accepted": True,
        "device_id": reading.device_id,
        "reading_number": reading.reading_number,
        "received_at": received_at.isoformat(),
    }


def process_sensor_data(
    reading: SensorReading,
    received_at: datetime,
) -> None:
    """
    Add the application's sensor-data handling here.

    This function could eventually:

    - Save the reading to a database
    - Update the current plant state
    - Calculate plant health
    - Detect dry soil
    - Trigger alerts
    - Update dashboard data
    - Send commands back to the Seeed device
    """

    # Sensor data processing will be added here.
    pass
