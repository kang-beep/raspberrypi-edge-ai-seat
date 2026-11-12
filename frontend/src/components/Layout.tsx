import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function Layout() {
  const { user, logout } = useAuth();
  const isAdmin = user?.role === "admin";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <strong>SmartSeat</strong>
          <span>{isAdmin ? "Admin console" : "User portal"}</span>
        </div>

        {user && (
          <div className="nav-groups">
            <nav className="nav-group" aria-label="사용자 메뉴">
              <span className="nav-group-label">사용자</span>
              <div className="nav">
                <NavLink to="/" end>
                  홈
                </NavLink>
                <NavLink to="/seats">좌석 예약</NavLink>
                <NavLink to="/profile">개인정보</NavLink>
              </div>
            </nav>

            {isAdmin && (
              <nav className="nav-group admin" aria-label="관리자 메뉴">
                <span className="nav-group-label">관리자</span>
                <div className="nav">
                  <NavLink to="/admin/seats">좌석 관리</NavLink>
                  <NavLink to="/admin/settings">설정</NavLink>
                </div>
              </nav>
            )}
          </div>
        )}

        {user && (
          <div className="topbar-user">
            <span className="muted">
              {user.full_name} ({user.role})
            </span>
            <button className="btn btn-secondary" type="button" onClick={logout}>
              로그아웃
            </button>
          </div>
        )}
      </header>
      <Outlet />
    </div>
  );
}
