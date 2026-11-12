from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai import face_ai_runtime
from app.api.auth import router as auth_router
from app.api.devices import router as devices_router
from app.api.seats import router as seats_router
from app.core.config import settings
from app.database.migrate import ensure_schema
from app.database.session import Base, SessionLocal, engine
from app.models import device as _device_model  # noqa: F401
from app.models import reservation as _reservation_model  # noqa: F401
from app.models import seat as _seat_model  # noqa: F401
from app.models import user as _user_model  # noqa: F401
from app.mqtt import handle_edge_message, mqtt_client
from app.services.auth_service import bootstrap_admin


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    ensure_schema(engine)
    db = SessionLocal()
    try:
        bootstrap_admin(db)
    finally:
        db.close()
    face_ai_runtime.start()
    mqtt_client.add_handler(handle_edge_message)
    mqtt_client.start()
    try:
        yield
    finally:
        mqtt_client.stop()
        face_ai_runtime.stop()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="REST API and WebSocket server for the smart seat system",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(seats_router)
app.include_router(devices_router)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "mqtt_connected": mqtt_client.connected,
    }
