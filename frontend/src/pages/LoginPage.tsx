import { useState } from "react";
import type { FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) {
    return <Navigate to={user.role === "admin" ? "/admin/seats" : "/"} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const next = await login({ username, password });
      navigate(next.role === "admin" ? "/admin/seats" : "/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그인 실패");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="auth-page">
      <form className="panel form-stack auth-card" onSubmit={handleSubmit}>
        <h1>로그인</h1>
        <p className="muted">사용자 또는 관리자 계정으로 로그인하세요.</p>
        <label>
          아이디
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label>
          비밀번호
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {error && <p className="field-error">{error}</p>}
        <button className="btn btn-primary" type="submit" disabled={busy}>
          {busy ? "로그인 중..." : "로그인"}
        </button>
        <p className="muted">
          계정이 없나요? <Link to="/register">회원가입</Link>
        </p>
      </form>
    </section>
  );
}
