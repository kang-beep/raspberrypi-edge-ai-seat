import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import {
  DEFAULT_ADMIN_SETTINGS,
  type AdminSettings,
} from "../types/domain";

const SETTINGS_STORAGE_KEY = "smartseat.adminSettings";

function loadSettings(): AdminSettings {
  const raw = window.localStorage.getItem(SETTINGS_STORAGE_KEY);
  if (!raw) {
    return DEFAULT_ADMIN_SETTINGS;
  }
  try {
    const parsed = JSON.parse(raw) as Partial<AdminSettings>;
    return {
      shortAwayGraceMinutes:
        Number(parsed.shortAwayGraceMinutes) ||
        DEFAULT_ADMIN_SETTINGS.shortAwayGraceMinutes,
      awayGraceMinutes:
        Number(parsed.awayGraceMinutes) ||
        DEFAULT_ADMIN_SETTINGS.awayGraceMinutes,
    };
  } catch {
    return DEFAULT_ADMIN_SETTINGS;
  }
}

export function SettingsPage() {
  const [settings, setSettings] = useState<AdminSettings>(DEFAULT_ADMIN_SETTINGS);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setSettings(loadSettings());
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    const next: AdminSettings = {
      shortAwayGraceMinutes: Math.max(1, settings.shortAwayGraceMinutes),
      awayGraceMinutes: Math.max(1, settings.awayGraceMinutes),
    };
    window.localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(next));
    setSettings(next);
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1500);
  }

  return (
    <section>
      <div className="page-header">
        <div>
          <h1>관리자 설정</h1>
          <p>자리비움 유예시간과 운영 파라미터를 설정합니다.</p>
        </div>
      </div>

      <form className="panel form-stack" onSubmit={handleSubmit}>
        <h2>이탈 유예시간</h2>
        <label>
          잠시 자리비움 유예 (분)
          <input
            type="number"
            min={1}
            value={settings.shortAwayGraceMinutes}
            onChange={(event) =>
              setSettings((current) => ({
                ...current,
                shortAwayGraceMinutes: Number(event.target.value),
              }))
            }
          />
        </label>
        <p className="muted">
          이용 중 → 잠시 자리비움 후, 이 시간이 지나면 자리비움으로 전환합니다.
        </p>
        <label>
          자리비움 유예 (분)
          <input
            type="number"
            min={1}
            value={settings.awayGraceMinutes}
            onChange={(event) =>
              setSettings((current) => ({
                ...current,
                awayGraceMinutes: Number(event.target.value),
              }))
            }
          />
        </label>
        <p className="muted">
          자리비움 후, 이 시간이 지나면 점유를 해제하고 비어 있음으로 전환합니다.
        </p>
        <div className="button-row">
          <button className="btn btn-primary" type="submit">
            저장
          </button>
          {saved && <span className="muted">저장됨</span>}
        </div>
      </form>

      <div className="panel" style={{ marginTop: "1rem" }}>
        <h2>상태 전환</h2>
        <p className="muted">
          이용 중 → 잠시 자리비움 → 자리비움 → 비어 있음
        </p>
      </div>
    </section>
  );
}
