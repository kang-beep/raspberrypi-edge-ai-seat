from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class SeatCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    device_id: str = Field(min_length=1, max_length=50)
    row: int | None = None
    col: int | None = None


class SeatUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    device_id: str | None = Field(default=None, max_length=50)
    active: bool | None = None
    status: str | None = None


class SeatPublic(BaseModel):
    id: int
    name: str
    row: int
    col: int
    device_id: str
    active: bool
    status: str
    current_user_id: int | None
    current_user_name: str | None = None
    updated_at: datetime
    reserved_by_me: bool = False
    is_reserved: bool = False

    model_config = {"from_attributes": True}


class ReservationCreate(BaseModel):
    starts_at: datetime
    ends_at: datetime

    @model_validator(mode="after")
    def validate_range(self) -> "ReservationCreate":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class ReservationPublic(BaseModel):
    id: int
    seat_id: int
    seat_name: str
    user_id: int
    user_name: str | None = None
    starts_at: datetime
    ends_at: datetime
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
