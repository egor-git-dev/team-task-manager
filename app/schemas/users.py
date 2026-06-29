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
    team_id: int | None


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8)
