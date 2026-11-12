from datetime import UTC, datetime

import numpy as np
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.storage import delete_enrollment_artifacts, save_enrollment_artifacts
from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    ProfileUpdateRequest,
    RegisterRequest,
)


def bootstrap_admin(db: Session) -> None:
    existing = db.scalar(
        select(User).where(User.username == settings.bootstrap_admin_username),
    )
    if existing is not None:
        return

    admin = User(
        username=settings.bootstrap_admin_username,
        password_hash=hash_password(settings.bootstrap_admin_password),
        full_name=settings.bootstrap_admin_name,
        email=None,
        phone=None,
        role="admin",
    )
    db.add(admin)
    db.commit()


def register_user(db: Session, payload: RegisterRequest) -> User:
    if payload.username == settings.bootstrap_admin_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is reserved",
        )
    exists = db.scalar(select(User).where(User.username == payload.username))
    if exists is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: LoginRequest) -> tuple[User, str]:
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(str(user.id), user.role)
    return user, token


def update_profile(db: Session, user: User, payload: ProfileUpdateRequest) -> User:
    user.full_name = payload.full_name
    user.email = payload.email
    user.phone = payload.phone
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def enroll_face(
    db: Session,
    user: User,
    crop_bgr: np.ndarray,
    embedding: np.ndarray,
) -> User:
    image_path, embedding_path = save_enrollment_artifacts(
        user.id,
        crop_bgr,
        embedding,
    )
    user.face_enrolled = True
    user.face_enrolled_at = datetime.now(UTC)
    user.face_image_path = image_path
    user.face_embedding_path = embedding_path
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_face(db: Session, user: User) -> User:
    if not user.face_enrolled and not user.face_image_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 얼굴이 없습니다.",
        )
    delete_enrollment_artifacts(user.face_image_path, user.face_embedding_path)
    user.face_enrolled = False
    user.face_enrolled_at = None
    user.face_image_path = None
    user.face_embedding_path = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
