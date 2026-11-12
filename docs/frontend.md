# Frontend (React Dashboard)

경로: `frontend/`

## 화면

| 경로 | 페이지 | 역할 |
| --- | --- | --- |
| `/` | 좌석 현황 | 배치도 + 4상태 통계 |
| `/users` | 사용자 등록 | 이름 입력, 프리뷰 자리, 등록 목록 |
| `/seats` | 좌석 관리 | 좌석/장치 ID 등록 |
| `/settings` | 관리자 설정 | 자리비움 유예시간 |

## 좌석 상태

| 값 | 표시 |
| --- | --- |
| `occupied` | 이용 중 |
| `short_away` | 잠시 자리비움 |
| `away` | 자리비움 |
| `empty` | 비어 있음 |

## 현재 상태

- mock 데이터 없음 (빈 상태에서 API 연동 예정)
- 설정값은 임시로 `localStorage` 저장
- WebSocket/REST 연결은 backend 구축 후 연결
