# SmartSeat 문서

## 문서 목록

| 문서 | 내용 |
| --- | --- |
| [architecture.md](./architecture.md) | 전체 구성과 상태 머신 |
| [backend.md](./backend.md) | PC FastAPI 서버 |
| [frontend.md](./frontend.md) | React 대시보드 |
| [mqtt.md](./mqtt.md) | EMQX MQTT 토픽/환경변수 |
| [raspberrypi-edge.md](./raspberrypi-edge.md) | Edge 개요 |
| [../raspberrypi-edge/docs/flows.md](../raspberrypi-edge/docs/flows.md) | 등록/입장/이탈 흐름과 예외 |

## Sparse Checkout

### PC 개발

```bash
git sparse-checkout init --cone
git sparse-checkout set backend frontend ai_training docs raspberrypi-edge
```

### Raspberry Pi 장치

```bash
git sparse-checkout init --cone
git sparse-checkout set raspberrypi-edge
```
