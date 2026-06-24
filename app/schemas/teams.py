from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    join_code: str
    created_at: datetime


class TeamJoin(BaseModel):
    join_code: str = Field(min_length=6, max_length=32)
