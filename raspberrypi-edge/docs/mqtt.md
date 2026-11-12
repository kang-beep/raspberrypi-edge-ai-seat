# MQTT (Edge)

Broker: EMQX Cloud Serverless  
Protocol: MQTT over TLS (`8883`)  
Library: `paho-mqtt` 2.x  

계정은 `.env`에만 둡니다. `.env.example`은 힌트만.

## 환경 변수

| Key | 설명 |
| --- | --- |
| `MQTT_HOST` | 브로커 호스트 |
| `MQTT_PORT` | `8883` |
| `MQTT_USERNAME` | EMQX 계정 |
| `MQTT_PASSWORD` | EMQX 비밀번호 |
| `MQTT_CLIENT_ID` | 장치마다 고유 (예: `smartseat-edge-raspi-a1`) |
| `MQTT_TOPIC_PREFIX` | 기본 `smartseat` |
| `MQTT_ENABLED` | `true` / `false` |
| `DEVICE_ID` | `raspi-a{n}` (예: `raspi-a1`) |
| `HEARTBEAT_INTERVAL_SECONDS` | 기본 `15` |

PC 서버 온라인 판정: health 미수신 **45초** → offline.

## 토픽

`{prefix}` = `MQTT_TOPIC_PREFIX`, `{device_id}` = `DEVICE_ID`

| 방향 | Topic | 용도 |
| --- | --- | --- |
| Edge → Server | `{prefix}/edge/{device_id}/health` | 하트비트·장치 등록 |
| Edge → Server | `{prefix}/edge/{device_id}/status` | 좌석 상태 |
| Edge → Server | `{prefix}/edge/{device_id}/events` | 체크인/거부 등 |
| Server → Edge | `{prefix}/server/{device_id}/commands` | ping, 예약 활성 등 |

예시 (`raspi-a1`):

```text
smartseat/edge/raspi-a1/health
smartseat/edge/raspi-a1/status
smartseat/edge/raspi-a1/events
smartseat/server/raspi-a1/commands
```

## 페이로드 예시

### health
```json
{"device_id":"raspi-a1","ok":true,"ts":"2026-11-12T07:00:00+00:00","status":"empty"}
```

### status
```json
{"device_id":"raspi-a1","status":"occupied","ts":"2026-11-12T07:00:00+00:00"}
```

### commands (현재)
```json
{"type":"ping","ts":"2026-11-12T07:00:00+00:00"}
```

향후 예정: `reservation_active` (user_id, embedding…), `reservation_end`
