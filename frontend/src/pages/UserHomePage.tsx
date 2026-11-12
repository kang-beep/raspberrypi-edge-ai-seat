import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function UserHomePage() {
  const { user } = useAuth();

  return (
    <section>
      <div className="page-header">
        <div>
          <h1>안녕하세요, {user?.full_name}</h1>
          <p>좌석 예약과 개인정보(얼굴 등록 포함)를 관리할 수 있습니다.</p>
        </div>
      </div>
      <div className="split-layout">
        <div className="panel">
          <h2>좌석 예약</h2>
          <p className="muted">배치도에서 빈 좌석을 선택해 예약하세요.</p>
          <Link className="btn btn-primary" to="/seats">
            예약하러 가기
          </Link>
        </div>
        <div className="panel">
          <h2>개인정보</h2>
          <p className="muted">
            {user?.face_enrolled
              ? "얼굴이 등록되어 있습니다. 정보를 수정할 수 있습니다."
              : "얼굴 등록 후 좌석을 예약할 수 있습니다."}
          </p>
          <Link className="btn btn-secondary" to="/profile#face">
            {user?.face_enrolled ? "개인정보 보기" : "얼굴 등록하기"}
          </Link>
        </div>
      </div>
    </section>
  );
}
