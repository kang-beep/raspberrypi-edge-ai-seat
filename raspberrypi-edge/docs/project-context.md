# Project Context (Edge Agent)

PC 모노레포의 Edge 파트입니다. 전체 시스템 이름은 SmartSeat입니다.

## 역할 분담

| 구성 | 역할 |
| --- | --- |
| Raspberry Pi 5 (`raspberrypi-edge`) | 초음파, 카메라, YuNet/SFace, 좌석 상태 판정, MQTT client |
| PC `backend` | FastAPI, SQLite, MQTT subscribe, devices/seats/reservations/face enroll |
| PC `frontend` | React 관리자/사용자 UI |
| EMQX Cloud | MQTT Broker (TLS 8883). Docker Mosquitto 없음 |

## 좌석 ↔ Pi 매핑

1. Pi 부팅 → `DEVICE_ID=raspi-a1` 등으로 `.../health` publish
2. PC가 `devices` 테이블에 upsert, 45초 미수신 시 offline
3. 관리자 웹에서 **온라인·미사용** 장치만 드롭다운으로 좌석에 연결
4. 사용 중 장치는 라벨 표시, **해제 후** 다른 좌석에 재연결

## MQTT (요약)

```text
smartseat/edge/{device_id}/health   # Edge → Server
smartseat/edge/{device_id}/status
smartseat/edge/{device_id}/events
smartseat/server/{device_id}/commands  # Server → Edge
```

상세: [mqtt.md](./mqtt.md)

## 착석/이탈 합의 시나리오

1. **예약 활성**일 때만 카메라 인증으로 `occupied` 가능  
2. 초음파: 책상–의자 사이 거리. 빈 의자 baseline보다 가까우면 착석 후보  
3. 디바운스 후 카메라 ON → YuNet → SFace → 예약자 임베딩 비교  
4. 일치 → `occupied` / 불일치·미검출 → occupied 금지 + events  
5. **이탈 후보(거리 멀어짐)** 도 얼굴 확인: 같은 사람 보이면 occupied 유지(의자 젖힘), 없으면 `short_away`  
6. 복귀(다시 가까움) 시 얼굴 재인증 후 occupied  
7. 예약 없이 앉음 → occupied 금지

주기 가이드: 초음파 ~0.5s 샘플, health 15s, 얼굴은 이벤트 기반(상시 연속 인식 아님).

## 영상 클립

인증 구간 녹화(카메라 ON ~ 인식 종료+2초)는 **보류**.  
전달은 MQTT 금지, 나중에 LAN HTTP 또는 VPN 등으로 검토.

## 소스 맵

```text
src/main.py              엔트리
src/config.py            .env 설정
src/mqtt/                TLS MQTT client, topics
src/sensors/presence.py  착석 감지 (현재 스텁 → HC-SR04 예정)
src/seat_monitoring/     heartbeat + status publish 루프
src/camera/              (예정)
src/ai_inference/        (예정) YuNet/SFace
src/enrollment/          (예정)
```

## PC와 맞춰야 하는 것

- 동일 EMQX 계정/호스트
- 동일 `MQTT_TOPIC_PREFIX` (기본 `smartseat`)
- 동일 `DEVICE_ID` 문자열
- PC 백엔드가 떠 있고 MQTT에 연결돼 있어야 웹 드롭다운에 장치가 보임

## HC-SR04 참고 배선 (BOARD)

- VCC → pin 2 (5V)
- TRIG → pin 11 (BCM 17)
- ECHO → pin 12 (BCM 18) + 전압 분배
- GND → pin 6  
라이브러리 예: `gpiozero.DistanceSensor` + `LGPIOFactory`
