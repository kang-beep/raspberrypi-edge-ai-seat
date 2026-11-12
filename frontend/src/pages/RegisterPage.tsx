import { useState } from "react";
import type { FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function RegisterPage() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register({
        username,
        password,
        full_name: fullName,
        email: email || undefined,
        phone: phone || undefined,
      });
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "회원가입 실패");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="auth-page">
      <form className="panel form-stack auth-card" onSubmit={handleSubmit}>
        <h1>회원가입</h1>
        <p className="muted">일반 사용자 계정을 생성합니다.</p>
        <label>
          아이디
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label>
          비밀번호
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        <label>
          이름
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
        </label>
        <label>
          이메일
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label>
          휴대폰
          <input value={phone} onChange={(e) => setPhone(e.target.value)} />
        </label>
        {error && <p className="field-error">{error}</p>}
        <button className="btn btn-primary" type="submit" disabled={busy}>
          {busy ? "가입 중..." : "가입하기"}
        </button>
        <p className="muted">
          이미 계정이 있나요? <Link to="/login">로그인</Link>
        </p>
      </form>
    </section>
  );
}
