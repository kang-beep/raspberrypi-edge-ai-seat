from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

EDGE_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = EDGE_ROOT / ".env"
MODELS_DIR = EDGE_ROOT / "models"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mqtt_enabled: bool = True
    mqtt_host: str = ""
    mqtt_port: int = 8883
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_client_id: str = "smartseat-edge-raspi-a1"
    mqtt_topic_prefix: str = "smartseat"

    device_id: str = "raspi-a1"
    seat_name: str = "Seat A1"
    camera_index: int = 0
    heartbeat_interval_seconds: int = 15


settings = Settings()
