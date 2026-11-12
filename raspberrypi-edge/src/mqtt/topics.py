from __future__ import annotations


def edge_health_topic(prefix: str, device_id: str) -> str:
    return f"{prefix}/edge/{device_id}/health"


def edge_status_topic(prefix: str, device_id: str) -> str:
    return f"{prefix}/edge/{device_id}/status"


def edge_events_topic(prefix: str, device_id: str) -> str:
    return f"{prefix}/edge/{device_id}/events"


def server_commands_topic(prefix: str, device_id: str) -> str:
    return f"{prefix}/server/{device_id}/commands"
