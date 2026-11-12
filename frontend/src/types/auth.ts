export type UserRole = "admin" | "user";

export interface AuthUser {
  id: number;
  username: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  role: UserRole;
  face_enrolled: boolean;
  face_enrolled_at: string | null;
  face_image_path: string | null;
  face_embedding_path: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  password: string;
  full_name: string;
  email?: string;
  phone?: string;
}

export interface ProfilePayload {
  full_name: string;
  email?: string;
  phone?: string;
}
