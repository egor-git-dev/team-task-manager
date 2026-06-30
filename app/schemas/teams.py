from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.users import UserRead


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime


class TeamJoin(BaseModel):
    join_code: str = Field(min_length=6, max_length=32)


class TeamWithMembersRead(TeamRead):
    users: list[UserRead]


class TeamWithJoinCodeRead(TeamRead):
    join_code: str


class TeamJoinCodeRead(BaseModel):
    join_code: str
