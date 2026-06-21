from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.users import UserRole


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
