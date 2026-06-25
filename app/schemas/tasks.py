from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.tasks import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    deadline: datetime | None = None
    assignee_id: int | None = Field(default=None, gt=0)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    deadline: datetime | None
    creator_id: int
    assignee_id: int | None
    team_id: int
    created_at: datetime


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    status: TaskStatus | None = None
    deadline: datetime | None = None
    assignee_id: int | None = Field(default=None, gt=0)
