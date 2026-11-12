# Pi에서 이 폴더 받기

PC 전체 모노레포가 아니라 **Edge만**  sparses checkout 하는 것을 권장합니다.

## Sparse checkout

```bash
git clone --filter=blob:none --sparse <REPO_URL> smartseat-edge
cd smartseat-edge
git sparse-checkout set raspberrypi-edge
cd raspberrypi-edge
```

또는 이미 clone된 저장소에서:

```bash
git sparse-checkout init --cone
git sparse-checkout set raspberrypi-edge
cd raspberrypi-edge
```

## 설정

```bash
cp .env.example .env
# MQTT_* , DEVICE_ID=raspi-a1 등 기입
uv sync
uv run python src/main.py
```

systemd: `deploy/smartseat-edge.service` 참고.

## Cursor on Pi

이 폴더를 워크스페이스 루트로 열면 `AGENTS.md`와 `.cursor/rules/`가 agent 컨텍스트로 쓰입니다.
