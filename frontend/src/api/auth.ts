import { apiRequest, apiRequestBlob, setAccessToken } from "./client";
import type {
  AuthUser,
  LoginPayload,
  ProfilePayload,
  RegisterPayload,
  TokenResponse,
} from "../types/auth";

export async function login(payload: LoginPayload): Promise<AuthUser> {
  const token = await apiRequest<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setAccessToken(token.access_token);
  return fetchMe();
}

export async function register(payload: RegisterPayload): Promise<AuthUser> {
  await apiRequest<AuthUser>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return login({
    username: payload.username,
    password: payload.password,
  });
}

export async function fetchMe(): Promise<AuthUser> {
  return apiRequest<AuthUser>("/api/auth/me");
}

export async function updateProfile(payload: ProfilePayload): Promise<AuthUser> {
  return apiRequest<AuthUser>("/api/auth/me", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function enrollFace(image: Blob): Promise<AuthUser> {
  const body = new FormData();
  body.append("file", image, "face.jpg");
  return apiRequest<AuthUser>("/api/auth/me/face", {
    method: "POST",
    body,
  });
}

export async function fetchMyFaceImage(): Promise<Blob> {
  return apiRequestBlob("/api/auth/me/face");
}

export async function deleteFace(): Promise<AuthUser> {
  return apiRequest<AuthUser>("/api/auth/me/face", {
    method: "DELETE",
  });
}

export function logout(): void {
  setAccessToken(null);
}
