from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.device import DevicePublic
from app.services import device_service

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("", response_model=list[DevicePublic])
def get_devices(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[DevicePublic]:
    rows = device_service.list_devices(db)
    return [DevicePublic.model_validate(row) for row in rows]
