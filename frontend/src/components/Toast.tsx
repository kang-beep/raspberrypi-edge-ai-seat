import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";

export type ToastTone = "info" | "success" | "error";

export interface ToastAction {
  label: string;
  to: string;
}

export interface ToastOptions {
  tone?: ToastTone;
  action?: ToastAction;
  durationMs?: number;
}

interface ToastItem {
  id: number;
  message: string;
  tone: ToastTone;
  action?: ToastAction;
  durationMs: number;
}

interface ToastContextValue {
  showToast: (message: string, options?: ToastOptions) => void;
}

const DEFAULT_DURATION_MS = 4500;
const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const dismiss = useCallback((id: number) => {
    setToasts((current) => current.filter((item) => item.id !== id));
  }, []);

  const showToast = useCallback((message: string, options?: ToastOptions) => {
    const id = Date.now() + Math.floor(Math.random() * 1000);
    setToasts((current) => [
      ...current,
      {
        id,
        message,
        tone: options?.tone ?? "info",
        action: options?.action,
        durationMs: options?.durationMs ?? DEFAULT_DURATION_MS,
      },
    ]);
  }, []);

  const value = useMemo(() => ({ showToast }), [showToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-viewport" aria-live="polite">
        {toasts.map((toast) => (
          <ToastCard key={toast.id} toast={toast} onDismiss={dismiss} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return context;
}

function ToastCard({
  toast,
  onDismiss,
}: {
  toast: ToastItem;
  onDismiss: (id: number) => void;
}) {
  useEffect(() => {
    const timer = window.setTimeout(() => onDismiss(toast.id), toast.durationMs);
    return () => window.clearTimeout(timer);
  }, [onDismiss, toast.durationMs, toast.id]);

  return (
    <div className={`toast toast-${toast.tone}`} role="status">
      <p>{toast.message}</p>
      <div className="toast-actions">
        {toast.action && (
          <Link
            className="btn btn-secondary toast-action"
            to={toast.action.to}
            onClick={() => onDismiss(toast.id)}
          >
            {toast.action.label}
          </Link>
        )}
        <button
          className="btn btn-secondary toast-action"
          type="button"
          onClick={() => onDismiss(toast.id)}
        >
          닫기
        </button>
      </div>
    </div>
  );
}
