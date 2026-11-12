# MQTT (EMQX Cloud)

Broker: EMQX Cloud Serverless  
Protocol: MQTT over TLS (`8883`)  
Library: `paho-mqtt` 2.x  

실제 값은 `.env`에 두고, `.env.example`은 키 힌트만 둡니다.  
`MQTT_USERNAME` / `MQTT_PASSWORD`는 직접 기입하세요.

## 환경 변수

| Key | 설명 |
| --- | --- |
| `MQTT_HOST` | 브로커 호스트 |
| `MQTT_PORT` | `8883` |
| `MQTT_USERNAME` | EMQX 인증 계정 |
| `MQTT_PASSWORD` | EMQX 인증 비밀번호 |
| `MQTT_CLIENT_ID` | 클라이언트 ID (장치마다 고유) |
| `MQTT_TOPIC_PREFIX` | 기본 `smartseat` |
| `MQTT_ENABLED` | `true`/`false` |
| `DEVICE_ID` (Edge) | `raspi-a{n}` 형식 (예: `raspi-a1`) |

Device ID 규칙: `raspi-a1`, `raspi-a2`, …  
Health 주기 15초, 서버 온라인 판정 **45초** (`DEVICE_ONLINE_TIMEOUT_SECONDS`).

## 토픽 (`{prefix}` = `MQTT_TOPIC_PREFIX`)

| 방향 | Topic | 용도 |
| --- | --- | --- |
| Edge → Server | `{prefix}/edge/{device_id}/health` | 하트비트 |
| Edge → Server | `{prefix}/edge/{device_id}/status` | 좌석 상태 |
| Edge → Server | `{prefix}/edge/{device_id}/events` | 체크인/거부 등 이벤트 |
| Server → Edge | `{prefix}/server/{device_id}/commands` | 설정/요청 명령 |

## 페이로드 예시

### health
```json
{"device_id":"raspi-a1","ok":true,"ts":"2026-11-12T07:00:00+00:00"}
```

### status
```json
{"device_id":"raspi-a1","status":"occupied","ts":"2026-11-12T07:00:00+00:00"}
```

### commands
```json
{"type":"ping","ts":"2026-11-12T07:00:00+00:00"}
```
