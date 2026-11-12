import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";
import { FaceEnrollPanel } from "../components/FaceEnrollPanel";
import { useToast } from "../components/Toast";
import type { EnrollmentPhase } from "../types/domain";

export function ProfilePage() {
  const { user, updateProfile, enrollFace, deleteFace } = useAuth();
  const { showToast } = useToast();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [busy, setBusy] = useState(false);
  const [faceBusy, setFaceBusy] = useState(false);
  const [phase, setPhase] = useState<EnrollmentPhase>("idle");
  const [faceRevision, setFaceRevision] = useState(0);

  useEffect(() => {
    if (!user) {
      return;
    }
    setFullName(user.full_name);
    setEmail(user.email ?? "");
    setPhone(user.phone ?? "");
    setPhase(user.face_enrolled ? "success" : "idle");
  }, [user]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setBusy(true);
    try {
      await updateProfile({
        full_name: fullName,
        email: email || undefined,
        phone: phone || undefined,
      });
      showToast("개인정보가 저장되었습니다.", { tone: "success" });
    } catch (err) {
      showToast(err instanceof Error ? err.message : "저장 실패", {
        tone: "error",
      });
    } finally {
      setBusy(false);
    }
  }

  async function handleFaceEnroll(image: Blob): Promise<void> {
    setFaceBusy(true);
    setPhase("capturing");
    try {
      await enrollFace(image);
      setFaceRevision((current) => current + 1);
      setPhase("success");
      showToast("얼굴 등록이 완료되었습니다.", { tone: "success" });
    } catch (err) {
      setPhase("failed");
      showToast(err instanceof Error ? err.message : "얼굴 등록 실패", {
        tone: "error",
      });
    } finally {
      setFaceBusy(false);
    }
  }

  async function handleFaceDelete(): Promise<void> {
    if (!window.confirm("등록된 얼굴 이미지와 특징을 삭제할까요?")) {
      return;
    }
    setFaceBusy(true);
    try {
      await deleteFace();
      setFaceRevision((current) => current + 1);
      setPhase("idle");
      showToast("얼굴 등록이 삭제되었습니다.", { tone: "success" });
    } catch (err) {
      showToast(err instanceof Error ? err.message : "얼굴 삭제 실패", {
        tone: "error",
      });
    } finally {
      setFaceBusy(false);
    }
  }

  if (!user) {
    return null;
  }

  return (
    <section className="profile-page">
      <div className="page-header">
        <div>
          <h1>개인정보</h1>
          <p>계정 정보와 얼굴 등록을 관리합니다.</p>
        </div>
      </div>

      <form className="panel form-stack profile-basic-panel" onSubmit={handleSubmit}>
        <h2>기본 정보</h2>
        <label>
          아이디
          <input value={user.username} disabled />
        </label>
        <label>
          이름
          <input
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            required
          />
        </label>
        <label>
          이메일
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>
        <label>
          휴대폰
          <input
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
          />
        </label>
        <button className="btn btn-primary" type="submit" disabled={busy}>
          {busy ? "저장 중..." : "저장"}
        </button>
      </form>

      <FaceEnrollPanel
        enrolled={user.face_enrolled}
        enrolledAt={user.face_enrolled_at}
        hasEnrolledImage={Boolean(user.face_enrolled && user.face_image_path)}
        imageRevision={faceRevision}
        busy={faceBusy}
        phase={phase}
        onEnroll={handleFaceEnroll}
        onDelete={handleFaceDelete}
        onPhaseChange={setPhase}
      />
    </section>
  );
}
