from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BACKEND_ROOT / "data" / "smartseat.db"
ENV_FILE = BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SmartSeat Backend"
    database_url: str = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
    secret_key: str = "smartseat-dev-secret-change-me"
    access_token_expire_minutes: int = 60 * 12
    cors_origins: list[str] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]
    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "1234"
    bootstrap_admin_name: str = "Administrator"

    mqtt_enabled: bool = True
    mqtt_host: str = ""
    mqtt_port: int = 8883
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_client_id: str = "smartseat-backend"
    mqtt_topic_prefix: str = "smartseat"
    device_online_timeout_seconds: int = 45


settings = Settings()
