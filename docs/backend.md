# Backend (PC 서버)

경로: `backend/`

## SQLite 구조 (`backend/data/smartseat.db`)

### `users`
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | INTEGER PK | |
| username | TEXT UNIQUE | 로그인 ID |
| password_hash | TEXT | bcrypt |
| full_name | TEXT | 이름 |
| email | TEXT NULL | |
| phone | TEXT NULL | |
| role | TEXT | `admin` / `user` |
| face_enrolled | BOOLEAN | 얼굴 등록 여부 |
| face_enrolled_at | DATETIME NULL | 얼굴 등록 시각 |
| face_image_path | TEXT NULL | `data/faces/...` 상대 경로 |
| face_embedding_path | TEXT NULL | `data/embeddings/...` 상대 경로 |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### `seats`
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | INTEGER PK | |
| name | TEXT UNIQUE | 좌석 이름 |
| row / col | INTEGER | 배치 좌표 |
| device_id | TEXT | 센서 ID |
| active | BOOLEAN | 운영 여부 |
| status | TEXT | `occupied` / `short_away` / `away` / `empty` |
| current_user_id | INTEGER NULL FK(users) | 현재 점유 사용자 |
| updated_at | DATETIME | |

### `reservations`
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | INTEGER PK | |
| seat_id | INTEGER FK(seats) | |
| user_id | INTEGER FK(users) | |
| starts_at / ends_at | DATETIME | 예약 구간 |
| status | TEXT | `reserved` / `checked_in` / `cancelled` / `completed` |
| created_at | DATETIME | |

## Auth

- bootstrap admin: `admin` / `1234`
- JWT bearer

## 주요 API

| Method | Path | 권한 |
| --- | --- | --- |
| POST | `/api/auth/register` | public |
| POST | `/api/auth/login` | public |
| GET/PUT | `/api/auth/me` | login |
| GET | `/api/auth/me/face` | login (등록된 얼굴 이미지) |
| POST | `/api/auth/me/face` | login (multipart `file` 이미지 필수) |
| DELETE | `/api/auth/me/face` | login (얼굴 등록 삭제) |

## Face AI

- 코드: `backend/app/ai/`
- 모델: `backend/ai/models/yunet/`, `backend/ai/models/sface/`
- 저장: `backend/data/faces/`, `backend/data/embeddings/`
- `main.py` 기동 시 모델 로드 + 단일 워커 추론 큐
- 검증: 얼굴 미검출 / score·crop 크기 / 블러 / SFace 임베딩 실패 시 400 + 한국어 `detail`

| GET | `/api/seats` | login |
| POST | `/api/seats` | admin |
| PATCH | `/api/seats/{id}` | admin |
| POST | `/api/seats/{id}/reservations` | login |
| GET | `/api/reservations/me` | login |
| POST | `/api/reservations/{id}/cancel` | login (본인/admin) |

## Devices

| Method | Path | 권한 |
| --- | --- | --- |
| GET | `/api/devices` | admin |
| POST | `/api/seats/{id}/unbind-device` | admin |

- 테이블: `devices` (`device_id`, `last_seen_at`)
- Edge `health` 수신 시 upsert
- 온라인: `last_seen` 기준 45초
- 좌석 생성/장치 연결: **온라인 & 미사용** 장치만 허용
- 사용 중 장치는 해제 후 재연결

## MQTT

- EMQX Cloud TLS (`8883`), `paho-mqtt` 2.x
- 설정: `backend/.env` (예시: `backend/.env.example`)
- 코드: `backend/app/mqtt/`
- 토픽: [mqtt.md](./mqtt.md)
- `main.py` 기동 시 연결
- Edge `health` → devices 등록, `status` → 매핑된 좌석 상태 갱신


## 실행

```bash
cd backend
cp .env.example .env   # 계정 기입
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

