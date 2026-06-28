from pydantic import BaseModel

from app.schemas.meetings import MeetingRead
from app.schemas.tasks import TaskRead


class CalendarRead(BaseModel):
    tasks: list[TaskRead]
    meetings: list[MeetingRead]
