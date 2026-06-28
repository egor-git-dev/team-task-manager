from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluationCreate(BaseModel):
    score: int = Field(ge=1, le=5)


class EvaluationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    evaluator_id: int
    user_id: int
    score: int
    created_at: datetime


class EvaluationAverageRead(BaseModel):
    average_score: float | None
    evaluations_count: int
