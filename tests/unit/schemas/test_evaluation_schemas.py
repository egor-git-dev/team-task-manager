import pytest
from pydantic import ValidationError

from app.schemas.evaluations import EvaluationCreate


def test_valid_score():
    evaluation = EvaluationCreate(score=4)

    assert evaluation.score == 4


def test_score_greater_than_5():
    with pytest.raises(ValidationError):
        EvaluationCreate(score=6)


def test_score_lower_than_1():
    with pytest.raises(ValidationError):
        EvaluationCreate(score=0)
