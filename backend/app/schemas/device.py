from datetime import datetime

from pydantic import BaseModel


class DevicePublic(BaseModel):
    device_id: str
    online: bool
    in_use: bool
    bound_seat_id: int | None = None
    bound_seat_name: str | None = None
    last_seen_at: datetime
    selectable: bool
