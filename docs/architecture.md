# 시스템 아키텍처

## 한 줄 요약

Raspberry Pi 5가 센서·카메라·AI로 좌석 상태를 판정하고,  
PC 서버가 MQTT(EMQX Cloud)로 받아 SQLite에 저장한 뒤 React 대시보드에 보여줍니다.

## 역할 분담

| 장치 | 담당 |
| --- | --- |
| Raspberry Pi 5 | 센서/카메라, YuNet 탐지, SFace 임베딩, 좌석 상태, MQTT client |
| PC 서버 | FastAPI, SQLite, MQTT client, WebSocket, React, AI 학습 |
| EMQX Cloud | MQTT Broker (TLS 8883) |

## AI 파이프라인

```text
카메라
  → YuNet: 얼굴 탐지 + crop
  → SFace: 임베딩 추출
  → 코사인 유사도 매칭
```

## 좌석 상태 머신

```text
empty
  → (예약 입장 승인) occupied
  → (이탈 감지) short_away
  → (shortAwayGrace 경과) away
  → (awayGrace 경과) empty
```

## 전체 파이프라인

```text
[Raspberry Pi 5]
  초음파 → 착석/이탈
  카메라 → YuNet → SFace
  seat_monitoring → 상태 판정
  MQTT publish

[EMQX Cloud]
  TLS MQTT Broker

[PC Server]
  MQTT subscribe → FastAPI → SQLite
  WebSocket/REST → React Dashboard
```

## 통신

| 구간 | 방식 | 용도 |
| --- | --- | --- |
| Pi ↔ PC | MQTT over TLS (EMQX Cloud) | 좌석/인식/헬스/명령 |
| Frontend → Backend | REST | 조회·등록·설정·좌석 관리 |
| Backend → Frontend | WebSocket | 실시간 좌석 현황 |

토픽 상세: [mqtt.md](./mqtt.md)

## 저장소

단일 GitHub 저장소 + sparse-checkout.

- PC 개발: `backend`, `frontend`, `ai_training`, `docs`, `raspberrypi-edge`
- Pi 장치: `raspberrypi-edge`
