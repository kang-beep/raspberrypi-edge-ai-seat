from __future__ import annotations

import json
import logging
import ssl
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from paho.mqtt.client import Client, MQTTMessage, MQTTv311
from paho.mqtt.enums import CallbackAPIVersion

from config import settings
from mqtt import topics

logger = logging.getLogger(__name__)
CommandHandler = Callable[[dict[str, Any]], None]


class EdgeMqttClient:
    def __init__(self) -> None:
        self._client: Client | None = None
        self._command_handlers: list[CommandHandler] = []

    def add_command_handler(self, handler: CommandHandler) -> None:
        self._command_handlers.append(handler)

    def start(self) -> None:
        if not settings.mqtt_enabled:
            logger.info("MQTT disabled")
            return
        if not settings.mqtt_host:
            raise RuntimeError("MQTT_HOST missing in .env")
        if not settings.mqtt_username or not settings.mqtt_password:
            raise RuntimeError("MQTT_USERNAME/PASSWORD missing in .env")
        if self._client is not None:
            return

        client = Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=settings.mqtt_client_id,
            protocol=MQTTv311,
        )
        client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        client.tls_insecure_set(False)
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.on_disconnect = self._on_disconnect
        client.connect(settings.mqtt_host, settings.mqtt_port, keepalive=60)
        client.loop_start()
        self._client = client
        logger.info("MQTT connecting to %s:%s", settings.mqtt_host, settings.mqtt_port)

    def stop(self) -> None:
        client = self._client
        if client is None:
            return
        client.loop_stop()
        client.disconnect()
        self._client = None

    def publish_health(self, ok: bool = True, **extra: Any) -> None:
        payload = {
            "device_id": settings.device_id,
            "ok": ok,
            "ts": _utc_now(),
            **extra,
        }
        self._publish(
            topics.edge_health_topic(settings.mqtt_topic_prefix, settings.device_id),
            payload,
        )

    def publish_status(self, status: str, **extra: Any) -> None:
        payload = {
            "device_id": settings.device_id,
            "status": status,
            "ts": _utc_now(),
            **extra,
        }
        self._publish(
            topics.edge_status_topic(settings.mqtt_topic_prefix, settings.device_id),
            payload,
        )

    def publish_event(self, event_type: str, **extra: Any) -> None:
        payload = {
            "device_id": settings.device_id,
            "type": event_type,
            "ts": _utc_now(),
            **extra,
        }
        self._publish(
            topics.edge_events_topic(settings.mqtt_topic_prefix, settings.device_id),
            payload,
        )

    def _publish(self, topic: str, payload: dict[str, Any], qos: int = 1) -> None:
        client = self._client
        if client is None or not client.is_connected():
            raise RuntimeError("MQTT client is not connected")
        body = json.dumps(payload, ensure_ascii=False)
        result = client.publish(topic, body, qos=qos)
        if result.rc != 0:
            raise RuntimeError(f"MQTT publish failed: rc={result.rc}")

    def _on_connect(
        self,
        client: Client,
        _userdata: object,
        _flags: object,
        reason_code: object,
        _properties: object | None = None,
    ) -> None:
        code = getattr(reason_code, "value", reason_code)
        if code != 0:
            logger.error("MQTT connect failed: %s", reason_code)
            return
        command_topic = topics.server_commands_topic(
            settings.mqtt_topic_prefix,
            settings.device_id,
        )
        client.subscribe(command_topic, qos=1)
        logger.info("MQTT connected; subscribed %s", command_topic)
        self.publish_health(ok=True, seat_name=settings.seat_name)

    def _on_disconnect(
        self,
        _client: Client,
        _userdata: object,
        _flags: object,
        reason_code: object,
        _properties: object | None = None,
    ) -> None:
        logger.warning("MQTT disconnected: %s", reason_code)

    def _on_message(
        self,
        _client: Client,
        _userdata: object,
        message: MQTTMessage,
    ) -> None:
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload must be object")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            logger.warning("Invalid command payload: %s", exc)
            return
        logger.info("Command received: %s", payload)
        if payload.get("type") == "ping":
            self.publish_health(ok=True, pong=True)
        for handler in self._command_handlers:
            handler(payload)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
