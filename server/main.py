from contextlib import asynccontextmanager

from fastapi import FastAPI
from api.health import router as health_router
from api.sensors import reset_display, router as sensor_router
from exceptions.handlers import register_exception_handlers
from web.routers import router as web_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    reset_display()
    yield


app = FastAPI(
    title="Plant Sensor Server",
    description="Receives plant sensor readings from Seeed devices.",
    version="1.0.0",
    lifespan=lifespan,
)


register_exception_handlers(app)

app.include_router(web_router)
app.include_router(sensor_router)
app.include_router(health_router)
