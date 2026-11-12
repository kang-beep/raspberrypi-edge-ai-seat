from __future__ import annotations

import json
import logging
import ssl
from collections.abc import Callable
from typing import Any

from paho.mqtt.client import Client, MQTTMessage, MQTTv311
from paho.mqtt.enums import CallbackAPIVersion

from app.core.config import settings
from app.mqtt import topics

logger = logging.getLogger(__name__)

MessageHandler = Callable[[str, dict[str, Any]], None]


class MqttClientService:
    def __init__(self) -> None:
        self._client: Client | None = None
        self._handlers: list[MessageHandler] = []

    @property
    def connected(self) -> bool:
        return self._client is not None and bool(self._client.is_connected())

    def add_handler(self, handler: MessageHandler) -> None:
        self._handlers.append(handler)

    def start(self) -> None:
        if not settings.mqtt_enabled:
            logger.info("MQTT disabled (MQTT_ENABLED=false)")
            return
        if not settings.mqtt_host:
            logger.warning("MQTT skipped: MQTT_HOST missing in .env")
            return
        if not settings.mqtt_username or not settings.mqtt_password:
            logger.warning("MQTT skipped: MQTT_USERNAME/PASSWORD missing in .env")
            return
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
        logger.info(
            "MQTT connecting to %s:%s",
            settings.mqtt_host,
            settings.mqtt_port,
        )

    def stop(self) -> None:
        client = self._client
        if client is None:
            return
        client.loop_stop()
        client.disconnect()
        self._client = None

    def publish(self, topic: str, payload: dict[str, Any], qos: int = 1) -> None:
        client = self._client
        if client is None or not client.is_connected():
            raise RuntimeError("MQTT client is not connected")
        body = json.dumps(payload, ensure_ascii=False)
        result = client.publish(topic, body, qos=qos)
        if result.rc != 0:
            raise RuntimeError(f"MQTT publish failed: rc={result.rc}")

    def publish_command(self, device_id: str, payload: dict[str, Any]) -> None:
        topic = topics.server_commands_topic(settings.mqtt_topic_prefix, device_id)
        self.publish(topic, payload)

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
        prefix = settings.mqtt_topic_prefix
        client.subscribe(
            [
                (topics.edge_health_filter(prefix), 1),
                (topics.edge_status_filter(prefix), 1),
                (topics.edge_events_filter(prefix), 1),
            ]
        )
        logger.info("MQTT connected and subscribed")

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
        topic = message.topic
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload must be a JSON object")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            logger.warning("Invalid MQTT payload on %s: %s", topic, exc)
            return
        for handler in self._handlers:
            try:
                handler(topic, payload)
            except Exception:  # noqa: BLE001 - isolate handler failures
                logger.exception("MQTT handler failed for %s", topic)


mqtt_client = MqttClientService()
