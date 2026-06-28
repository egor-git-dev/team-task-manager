from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MeetingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    starts_at: datetime
    ends_at: datetime
    participant_id: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_time_range(self) -> "MeetingCreate":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be greater than starts_at")
        return self


class MeetingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    starts_at: datetime
    ends_at: datetime
    creator_id: int
    participant_id: int
    team_id: int
    is_cancelled: bool
    created_at: datetime
