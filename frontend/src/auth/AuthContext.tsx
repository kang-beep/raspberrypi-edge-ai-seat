import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";
import * as authApi from "../api/auth";
import { getAccessToken } from "../api/client";
import type {
  AuthUser,
  LoginPayload,
  ProfilePayload,
  RegisterPayload,
} from "../types/auth";

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (payload: LoginPayload) => Promise<AuthUser>;
  register: (payload: RegisterPayload) => Promise<AuthUser>;
  updateProfile: (payload: ProfilePayload) => Promise<AuthUser>;
  enrollFace: (image: Blob) => Promise<AuthUser>;
  deleteFace: () => Promise<AuthUser>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }
    authApi
      .fetchMe()
      .then(setUser)
      .catch(() => authApi.logout())
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const next = await authApi.login(payload);
    setUser(next);
    return next;
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    const next = await authApi.register(payload);
    setUser(next);
    return next;
  }, []);

  const updateProfile = useCallback(async (payload: ProfilePayload) => {
    const next = await authApi.updateProfile(payload);
    setUser(next);
    return next;
  }, []);

  const enrollFace = useCallback(async (image: Blob) => {
    const next = await authApi.enrollFace(image);
    setUser(next);
    return next;
  }, []);

  const deleteFace = useCallback(async () => {
    const next = await authApi.deleteFace();
    setUser(next);
    return next;
  }, []);

  const logout = useCallback(() => {
    authApi.logout();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      updateProfile,
      enrollFace,
      deleteFace,
      logout,
    }),
    [
      user,
      loading,
      login,
      register,
      updateProfile,
      enrollFace,
      deleteFace,
      logout,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
