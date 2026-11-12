# Raspberry Pi Edge

상세 코드/문서는 `raspberrypi-edge/` 폴더를 기준으로 합니다.

- 개요: [`../raspberrypi-edge/README.md`](../raspberrypi-edge/README.md)
- 흐름/예외: [`../raspberrypi-edge/docs/flows.md`](../raspberrypi-edge/docs/flows.md)
- MQTT: [mqtt.md](./mqtt.md)

## 요약

- Broker: EMQX Cloud (TLS)
- Pi는 MQTT client
- 탐지: YuNet / 임베딩: SFace
- 상태: `occupied` → `short_away` → `away` → `empty`
- systemd 예시: `raspberrypi-edge/deploy/smartseat-edge.service`
