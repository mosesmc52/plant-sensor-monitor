from pydantic import BaseModel, Field

# ------------------------------------------------------------
# Sensor Data Model
# ------------------------------------------------------------


class SensorReading(BaseModel):
    device_id: str = Field(
        min_length=1,
        max_length=100,
        examples=["plant-sensor-01"],
    )

    reading_number: int = Field(
        ge=0,
        examples=[1],
    )

    temperature_f: float = Field(
        ge=-100,
        le=200,
        examples=[72.5],
    )

    humidity_percent: float = Field(
        ge=0,
        le=100,
        examples=[52.4],
    )

    light_lux: float = Field(
        ge=0,
        examples=[450.0],
    )

    moisture_1_percent: int = Field(
        ge=0,
        le=100,
        examples=[64],
    )

    moisture_2_percent: int = Field(
        ge=0,
        le=100,
        examples=[58],
    )

    uptime_seconds: int = Field(
        ge=0,
        examples=[120],
    )
