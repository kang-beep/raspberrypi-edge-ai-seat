# Raspberry Pi Edge (SmartSeat)

PC 서버와 분리되는 Edge 실행 영역입니다.  
Pi에서는 이 폴더만 sparse-checkout으로 가져가면 됩니다.

**Cursor / AI agent:** 먼저 [AGENTS.md](./AGENTS.md)와 [docs/project-context.md](./docs/project-context.md)를 읽으세요.

## 역할

- 초음파 센서로 착석/이탈 감지
- 카메라 촬영
- YuNet 얼굴 탐지 및 crop
- SFace 임베딩 추출/비교
- MQTT(EMQX Cloud TLS)로 PC 서버에 이벤트 전송

## 올바른 AI 파이프라인

```text
카메라 프레임
  → YuNet: 얼굴 탐지 + crop
  → SFace: 임베딩(특징 벡터) 추출
  → (입장 시) 예약 사용자 임베딩과 코사인 유사도 비교
```

## 좌석 상태

| 상태 | 의미 |
| --- | --- |
| `occupied` | 이용 중 |
| `short_away` | 잠시 자리비움 |
| `away` | 자리비움 |
| `empty` | 비어 있음 |

```text
empty
  → (예약 입장 + 얼굴 승인) occupied
  → (이탈 확정) short_away
  → (shortAwayGrace 경과) away
  → (awayGrace 경과) empty
```

Device ID: `raspi-a{n}` (예: `raspi-a1`)

## 문서

| 문서 | 내용 |
| --- | --- |
| [AGENTS.md](./AGENTS.md) | Cursor agent 가이드 |
| [docs/project-context.md](./docs/project-context.md) | 설계·구현 상태 |
| [docs/mqtt.md](./docs/mqtt.md) | MQTT 토픽 |
| [docs/flows.md](./docs/flows.md) | 운영 흐름·예외 |
| [docs/setup-on-pi.md](./docs/setup-on-pi.md) | Pi clone/실행 |

## 빠른 실행

```bash
cd raspberrypi-edge
cp .env.example .env   # EMQX 계정·DEVICE_ID=raspi-a1 기입
uv sync
uv run python src/main.py
```

## 디렉터리

```text
raspberrypi-edge/
├── AGENTS.md
├── .cursor/rules/
├── docs/
├── deploy/
├── src/
├── models/
├── .env.example
└── pyproject.toml
```
