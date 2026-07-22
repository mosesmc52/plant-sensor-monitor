from fastapi import FastAPI
from api.health import router as health_router
from api.sensors import router as sensor_router
from exceptions.handlers import register_exception_handlers
from web.routers import router as web_router

app = FastAPI(
    title="Plant Sensor Server",
    description="Receives plant sensor readings from Seeed devices.",
    version="1.0.0",
)


register_exception_handlers(app)

app.include_router(web_router)
app.include_router(sensor_router)
app.include_router(health_router)
