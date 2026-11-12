import { useEffect, useRef, useState } from "react";
import type { ChangeEvent } from "react";
import { fetchMyFaceImage } from "../api/auth";
import { StatusBadge } from "./StatusBadge";
import type { EnrollmentPhase } from "../types/domain";
import { formatTimestamp } from "../utils/format";

interface FaceEnrollPanelProps {
  enrolled: boolean;
  enrolledAt: string | null;
  hasEnrolledImage: boolean;
  imageRevision: number;
  busy: boolean;
  phase: EnrollmentPhase;
  onEnroll: (image: Blob) => Promise<void>;
  onDelete: () => Promise<void>;
  onPhaseChange: (phase: EnrollmentPhase) => void;
}

const PHASE_COPY: Record<EnrollmentPhase, string> = {
  idle: "웹캠 촬영 또는 이미지 업로드 후 등록하세요.",
  waiting_capture: "이미지를 준비하는 중입니다.",
  capturing: "얼굴을 검증하는 중입니다.",
  success: "얼굴 등록이 완료되었습니다.",
  failed: "등록에 실패했습니다. 다른 사진으로 다시 시도하세요.",
};

export function FaceEnrollPanel({
  enrolled,
  enrolledAt,
  hasEnrolledImage,
  imageRevision,
  busy,
  phase,
  onEnroll,
  onDelete,
  onPhaseChange,
}: FaceEnrollPanelProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [cameraOn, setCameraOn] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [enrolledUrl, setEnrolledUrl] = useState<string | null>(null);
  const [pendingImage, setPendingImage] = useState<Blob | null>(null);
  const [cameraError, setCameraError] = useState("");

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    };
  }, []);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  useEffect(() => {
    setPendingImage(null);
    setPreviewUrl((current) => {
      if (current) {
        URL.revokeObjectURL(current);
      }
      return null;
    });
  }, [imageRevision]);

  useEffect(() => {
    let active = true;
    let objectUrl: string | null = null;

    async function loadEnrolledImage(): Promise<void> {
      if (!hasEnrolledImage) {
        setEnrolledUrl(null);
        return;
      }
      try {
        const blob = await fetchMyFaceImage();
        if (!active) {
          return;
        }
        objectUrl = URL.createObjectURL(blob);
        setEnrolledUrl(objectUrl);
      } catch {
        if (active) {
          setEnrolledUrl(null);
        }
      }
    }

    void loadEnrolledImage();
    return () => {
      active = false;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [hasEnrolledImage, imageRevision]);

  useEffect(() => {
    const video = videoRef.current;
    const stream = streamRef.current;
    if (!cameraOn || !video || !stream) {
      return;
    }
    video.srcObject = stream;
    void video.play().catch(() => {
      setCameraError("웹캠 재생에 실패했습니다.");
    });
  }, [cameraOn]);

  async function startCamera(): Promise<void> {
    setCameraError("");
    try {
      stopCamera();
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
        audio: false,
      });
      streamRef.current = stream;
      setCameraOn(true);
    } catch {
      setCameraOn(false);
      setCameraError("웹캠을 사용할 수 없습니다. 이미지 업로드를 이용하세요.");
    }
  }

  function stopCamera(): void {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraOn(false);
  }

  function setImage(blob: Blob): void {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPendingImage(blob);
    setPreviewUrl(URL.createObjectURL(blob));
    onPhaseChange("idle");
  }

  async function captureFromCamera(): Promise<void> {
    const video = videoRef.current;
    if (!cameraOn || !video || video.readyState < 2) {
      setCameraError("먼저 웹캠을 켜주세요.");
      return;
    }
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    if (!context) {
      return;
    }
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise<Blob | null>((resolve) => {
      canvas.toBlob((value) => resolve(value), "image/jpeg", 0.92);
    });
    if (!blob) {
      setCameraError("촬영에 실패했습니다.");
      return;
    }
    setCameraError("");
    setImage(blob);
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>): void {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    if (!file.type.startsWith("image/")) {
      setCameraError("이미지 파일만 업로드할 수 있습니다.");
      return;
    }
    setCameraError("");
    stopCamera();
    setImage(file);
  }

  async function handleEnroll(): Promise<void> {
    if (!pendingImage || busy) {
      return;
    }
    onPhaseChange("capturing");
    await onEnroll(pendingImage);
  }

  const statusText =
    enrolled && phase === "success" && enrolledAt
      ? `${PHASE_COPY.success} · ${formatTimestamp(enrolledAt)}`
      : PHASE_COPY[phase];

  return (
    <div id="face" className="panel face-enroll-panel">
      <div className="page-header compact">
        <div>
          <h2>내 얼굴 등록</h2>
          <p className="muted">{statusText}</p>
        </div>
        <StatusBadge tone={faceBadgeTone(enrolled, phase)} />
      </div>

      {cameraError && <p className="field-error face-enroll-error">{cameraError}</p>}

      <div className="face-enroll-layout">
        <div className="face-stage">
          {cameraOn ? (
            <video
              className="face-stage-media"
              ref={videoRef}
              muted
              playsInline
            />
          ) : previewUrl ? (
            <>
              <img
                className="face-stage-media"
                src={previewUrl}
                alt="등록할 얼굴 미리보기"
              />
              <span className="face-stage-caption">새 등록 후보</span>
            </>
          ) : enrolledUrl ? (
            <>
              <img
                className="face-stage-media"
                src={enrolledUrl}
                alt="등록된 내 얼굴"
              />
              <span className="face-stage-caption">등록된 얼굴</span>
            </>
          ) : (
            <div className="face-stage-empty">
              <strong>미리보기</strong>
              <span>웹캠을 켜거나 이미지를 업로드하세요.</span>
            </div>
          )}
        </div>

        <div className="face-enroll-actions">
          <div className="face-action-group">
            <span className="face-action-label">입력</span>
            <div className="button-row face-action-row">
              {cameraOn ? (
                <button
                  className="btn btn-secondary"
                  type="button"
                  onClick={stopCamera}
                  disabled={busy}
                >
                  웹캠 끄기
                </button>
              ) : (
                <button
                  className="btn btn-secondary"
                  type="button"
                  onClick={() => void startCamera()}
                  disabled={busy}
                >
                  웹캠 켜기
                </button>
              )}
              <button
                className="btn btn-secondary"
                type="button"
                onClick={() => void captureFromCamera()}
                disabled={busy || !cameraOn}
              >
                촬영
              </button>
              <label
                className={`btn btn-secondary file-button${busy ? " is-disabled" : ""}`}
              >
                이미지 업로드
                <input
                  type="file"
                  accept="image/*"
                  hidden
                  onChange={handleFileChange}
                  disabled={busy}
                />
              </label>
            </div>
          </div>

          <div className="face-action-group">
            <span className="face-action-label">등록</span>
            <button
              className="btn btn-primary face-enroll-submit"
              type="button"
              onClick={() => void handleEnroll()}
              disabled={busy || !pendingImage}
            >
              {busy ? "등록 중..." : enrolled ? "다시 등록" : "등록하기"}
            </button>
            {enrolled && (
              <button
                className="btn btn-danger face-enroll-submit"
                type="button"
                onClick={() => void onDelete()}
                disabled={busy}
              >
                등록 삭제
              </button>
            )}
            {!pendingImage && (
              <p className="muted face-hint">
                촬영하거나 업로드한 이미지가 있어야 등록할 수 있습니다.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function faceBadgeTone(
  enrolled: boolean,
  phase: EnrollmentPhase,
): "ready" | "pending" | "failed" | "unenrolled" {
  if (enrolled || phase === "success") {
    return "ready";
  }
  if (phase === "failed") {
    return "failed";
  }
  if (phase === "waiting_capture" || phase === "capturing") {
    return "pending";
  }
  return "unenrolled";
}
