import pytest
from pydantic import ValidationError

from app.schemas.tasks import TaskCreate, TaskUpdate


def test_valid_task():
    task = TaskCreate(title="Do some work", description="A little bit work")

    assert task.title == "Do some work"
    assert task.description == "A little bit work"


def test_invalid_task_title():
    with pytest.raises(ValidationError):
        TaskCreate(title="", description="A little bit work")


def test_update_task_invalid_title():
    with pytest.raises(ValidationError):
        TaskUpdate(title="")


def test_assignee_id_must_be_positive():
    with pytest.raises(ValidationError):
        TaskCreate(title="Do some work", description="A little bit work", assignee_id=0)
