from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluations import Evaluation
from app.models.tasks import Task, TaskStatus
from app.models.users import User, UserRole
from app.schemas.evaluations import EvaluationCreate
from app.services import evaluations as evaluation_services
from app.services import tasks as task_services


@pytest.mark.asyncio
async def test_create_evaluation_success(monkeypatch):
    task = Task(id=1, status=TaskStatus.DONE, assignee_id=2, team_id=1)
    current_user = User(id=3, team_id=1, role=UserRole.MANAGER)
    evaluation_data = EvaluationCreate(score=5)
    evaluation = Evaluation(
        id=1,
        task_id=task.id,
        evaluator_id=current_user.id,
        user_id=task.assignee_id,
        score=evaluation_data.score,
    )

    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    mock_get_evaluation_by_task_id = AsyncMock(return_value=None)
    mock_create_evaluation = AsyncMock(return_value=evaluation)

    monkeypatch.setattr(
        evaluation_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "get_evaluation_by_task_id",
        mock_get_evaluation_by_task_id,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "create_evaluation",
        mock_create_evaluation,
    )

    db = AsyncMock(spec=AsyncSession)

    result = await evaluation_services.create_evaluation(
        task.id,
        evaluation_data,
        current_user,
        db,
    )

    assert result is evaluation
    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_get_evaluation_by_task_id.assert_awaited_once_with(task.id, db)
    mock_create_evaluation.assert_awaited_once_with(
        task.id,
        current_user.id,
        task.assignee_id,
        evaluation_data,
        db,
    )


@pytest.mark.asyncio
async def test_create_evaluation_task_not_found_error(monkeypatch):
    task = Task(id=1, status=TaskStatus.DONE, assignee_id=2, team_id=1)
    current_user = User(id=3, team_id=1, role=UserRole.MANAGER)
    evaluation_data = EvaluationCreate(score=5)

    mock_get_task_by_id_for_user_or_raise = AsyncMock(
        side_effect=task_services.TaskNotFoundError()
    )
    mock_get_evaluation_by_task_id = AsyncMock()
    mock_create_evaluation = AsyncMock()

    monkeypatch.setattr(
        evaluation_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "get_evaluation_by_task_id",
        mock_get_evaluation_by_task_id,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "create_evaluation",
        mock_create_evaluation,
    )

    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskNotFoundError):
        await evaluation_services.create_evaluation(
            task.id,
            evaluation_data,
            current_user,
            db,
        )

    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_get_evaluation_by_task_id.assert_not_awaited()
    mock_create_evaluation.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_evaluation_permission_error(monkeypatch):
    task = Task(id=1, status=TaskStatus.DONE, assignee_id=2, team_id=1)
    current_user = User(id=3, team_id=1, role=UserRole.USER)
    evaluation_data = EvaluationCreate(score=5)

    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    mock_get_evaluation_by_task_id = AsyncMock()
    mock_create_evaluation = AsyncMock()

    monkeypatch.setattr(
        evaluation_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "get_evaluation_by_task_id",
        mock_get_evaluation_by_task_id,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "create_evaluation",
        mock_create_evaluation,
    )

    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(evaluation_services.EvaluationPermissionError):
        await evaluation_services.create_evaluation(
            task.id,
            evaluation_data,
            current_user,
            db,
        )

    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_get_evaluation_by_task_id.assert_not_awaited()
    mock_create_evaluation.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_evaluation_task_not_done_error(monkeypatch):
    task = Task(id=1, status=TaskStatus.OPEN, assignee_id=2, team_id=1)
    current_user = User(id=3, team_id=1, role=UserRole.MANAGER)
    evaluation_data = EvaluationCreate(score=5)

    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    mock_get_evaluation_by_task_id = AsyncMock()
    mock_create_evaluation = AsyncMock()

    monkeypatch.setattr(
        evaluation_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "get_evaluation_by_task_id",
        mock_get_evaluation_by_task_id,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "create_evaluation",
        mock_create_evaluation,
    )

    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(evaluation_services.TaskNotDoneError):
        await evaluation_services.create_evaluation(
            task.id,
            evaluation_data,
            current_user,
            db,
        )

    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_get_evaluation_by_task_id.assert_not_awaited()
    mock_create_evaluation.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_evaluation_task_has_no_assignee_error(monkeypatch):
    task = Task(id=1, status=TaskStatus.DONE, assignee_id=None, team_id=1)
    current_user = User(id=3, team_id=1, role=UserRole.MANAGER)
    evaluation_data = EvaluationCreate(score=5)

    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    mock_get_evaluation_by_task_id = AsyncMock()
    mock_create_evaluation = AsyncMock()

    monkeypatch.setattr(
        evaluation_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "get_evaluation_by_task_id",
        mock_get_evaluation_by_task_id,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "create_evaluation",
        mock_create_evaluation,
    )

    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(evaluation_services.TaskHasNoAssigneeError):
        await evaluation_services.create_evaluation(
            task.id,
            evaluation_data,
            current_user,
            db,
        )

    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_get_evaluation_by_task_id.assert_not_awaited()
    mock_create_evaluation.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_evaluation_already_exists(monkeypatch):
    task = Task(id=1, status=TaskStatus.DONE, assignee_id=3, team_id=1)
    current_user = User(id=3, team_id=1, role=UserRole.MANAGER)
    evaluation_data = EvaluationCreate(score=5)
    evaluation = Evaluation(
        id=1,
        task_id=task.id,
        evaluator_id=current_user.id,
        user_id=task.assignee_id,
        score=evaluation_data.score,
    )

    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    mock_get_evaluation_by_task_id = AsyncMock(return_value=evaluation)
    mock_create_evaluation = AsyncMock()

    monkeypatch.setattr(
        evaluation_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "get_evaluation_by_task_id",
        mock_get_evaluation_by_task_id,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "create_evaluation",
        mock_create_evaluation,
    )

    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(evaluation_services.EvaluationAlreadyExistsError):
        await evaluation_services.create_evaluation(
            task.id,
            evaluation_data,
            current_user,
            db,
        )

    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_get_evaluation_by_task_id.assert_awaited_once_with(task.id, db)
    mock_create_evaluation.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_current_user_evaluations(monkeypatch):
    current_user = User(id=1)
    evaluations = [
        Evaluation(id=1, task_id=1, evaluator_id=2, user_id=1, score=4),
        Evaluation(id=2, task_id=2, evaluator_id=3, user_id=1, score=5),
    ]

    mock_get_user_evaluations = AsyncMock(return_value=evaluations)
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "get_user_evaluations",
        mock_get_user_evaluations,
    )

    db = AsyncMock(spec=AsyncSession)

    result = await evaluation_services.get_current_user_evaluations(
        current_user,
        db,
    )

    assert result is evaluations
    mock_get_user_evaluations.assert_awaited_once_with(current_user.id, db)


@pytest.mark.asyncio
async def test_get_current_user_average_score(monkeypatch):
    current_user = User(id=1)

    mock_get_user_average_score = AsyncMock(return_value=4.5)
    mock_get_user_evaluations_count = AsyncMock(return_value=2)

    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "get_user_average_score",
        mock_get_user_average_score,
    )
    monkeypatch.setattr(
        evaluation_services.evaluation_crud,
        "get_user_evaluations_count",
        mock_get_user_evaluations_count,
    )

    db = AsyncMock(spec=AsyncSession)

    result = await evaluation_services.get_current_user_average_score(
        current_user,
        db,
    )

    assert result.average_score == 4.5
    assert result.evaluations_count == 2
    mock_get_user_average_score.assert_awaited_once_with(current_user.id, db)
    mock_get_user_evaluations_count.assert_awaited_once_with(current_user.id, db)
