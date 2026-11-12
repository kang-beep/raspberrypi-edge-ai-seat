# SmartSeat Edge — Agent Guide

이 폴더는 **Raspberry Pi 5 Edge 런타임만** 담습니다.  
PC의 FastAPI/React/SQLite는 여기 없습니다. Cursor agent는 이 문서를 먼저 읽고 작업하세요.

## 한 줄 요약

Pi가 초음파·카메라·YuNet/SFace로 좌석을 판정하고, **EMQX Cloud MQTT(TLS)** 로 PC 서버와 통신합니다.

## 필수 문서

| 문서 | 내용 |
| --- | --- |
| [README.md](./README.md) | 역할, 실행 방법 |
| [docs/project-context.md](./docs/project-context.md) | 전체 아키텍처·합의된 설계·구현 상태 |
| [docs/mqtt.md](./docs/mqtt.md) | 토픽·페이로드·device_id |
| [docs/flows.md](./docs/flows.md) | 등록/입장/이탈·예외 |
| [docs/setup-on-pi.md](./docs/setup-on-pi.md) | Pi에서 clone/실행 |

## Device ID

- 형식: `raspi-a{n}` → `raspi-a1`, `raspi-a2`, …
- `.env`의 `DEVICE_ID`와 MQTT 토픽·PC `devices`/`seats.device_id`가 **동일 문자열**이어야 함

## 코딩 규칙 (Edge)

- 언어: Python 3.11+, type hints 필수
- 함수 30줄 이하, early return, 매직넘버는 상수/`.env`
- 비밀값: `.env`만 (gitignore). `.env.example`은 힌트만
- MQTT: `paho-mqtt` 2.x, TLS 8883
- 영상 파일을 MQTT로 보내지 말 것 (나중에 HTTP/VPN 등 별도 설계)
- 거리만으로 이탈/재착석 확정 금지 → **얼굴 확인과 함께** (의자 젖힘 오탐 방지)

## 현재 구현 vs 다음 작업

**됨:** MQTT 클라이언트, health/status publish, commands(ping) 구독, presence 스텁, seat monitor heartbeat

**다음:** HC-SR04 실연동, 예약 임베딩 수신, 얼굴 입장/이탈 인증, 센서 로그, (나중) 인증 구간 녹화

## 응답 언어

사용자와는 **한국어**, 코드·주석·커밋 메시지는 **영어**.
