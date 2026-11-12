from datetime import datetime

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    username: str
    full_name: str
    email: str | None
    phone: str | None
    role: str
    face_enrolled: bool
    face_enrolled_at: datetime | None
    face_image_path: str | None
    face_embedding_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=72)
    full_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=30)


class LoginRequest(BaseModel):
    username: str
    password: str


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
