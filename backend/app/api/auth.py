from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.ai import FaceQualityError, face_ai_runtime
from app.ai.config import ALLOWED_CONTENT_TYPES, DATA_ROOT, MAX_UPLOAD_BYTES
from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from app.services.auth_service import (
    authenticate_user,
    delete_face,
    enroll_face,
    register_user,
    update_profile,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    return register_user(db, payload)


@router.post("/login", response_model=TokenResponse)
def login_json(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    _, token = authenticate_user(db, payload)
    return TokenResponse(access_token=token)


@router.post("/token", response_model=TokenResponse)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    _, token = authenticate_user(
        db,
        LoginRequest(username=form_data.username, password=form_data.password),
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.put("/me", response_model=UserPublic)
def update_me(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    return update_profile(db, current_user, payload)


@router.get("/me/face")
def get_my_face(
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    image_path = _resolve_face_image_path(current_user)
    return FileResponse(image_path, media_type="image/jpeg")


@router.post("/me/face", response_model=UserPublic)
async def enroll_my_face(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    image_bytes = await _read_face_upload(file)
    try:
        result = await face_ai_runtime.enroll(image_bytes)
    except FaceQualityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="얼굴 처리 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.",
        ) from exc
    return enroll_face(db, current_user, result.crop_bgr, result.embedding)


@router.delete("/me/face", response_model=UserPublic)
def delete_my_face(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    return delete_face(db, current_user)


def _resolve_face_image_path(user: User) -> Path:
    if not user.face_enrolled or not user.face_image_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 얼굴 이미지가 없습니다.",
        )
    candidate = (DATA_ROOT / user.face_image_path).resolve()
    faces_root = (DATA_ROOT / "faces").resolve()
    try:
        candidate.relative_to(faces_root)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 얼굴 이미지를 찾을 수 없습니다.",
        ) from exc
    if not candidate.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 얼굴 이미지를 찾을 수 없습니다.",
        )
    return candidate


async def _read_face_upload(file: UploadFile) -> bytes:
    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="지원하지 않는 이미지 형식입니다. JPG/PNG로 올려주세요.",
        )
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지 파일이 비어 있습니다.",
        )
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지 용량이 너무 큽니다. 8MB 이하로 올려주세요.",
        )
    return image_bytes
