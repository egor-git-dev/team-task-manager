from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.models.evaluations import Evaluation
from app.models.users import User, UserRole
from app.schemas.evaluations import EvaluationAverageRead
from app.services import evaluations as evaluation_services
from app.services import tasks as task_services

client = TestClient(app)


def test_create_evaluation_success(monkeypatch):
    evaluation = Evaluation(
        id=1,
        task_id=5,
        evaluator_id=2,
        user_id=3,
        score=4,
        created_at=datetime.now(UTC),
    )

    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    mock_create_evaluation = AsyncMock(return_value=evaluation)
    monkeypatch.setattr(
        evaluation_services,
        "create_evaluation",
        mock_create_evaluation,
    )

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/evaluations/tasks/5",
            json={"score": 4},
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert data["task_id"] == 5
    assert data["evaluator_id"] == 2
    assert data["user_id"] == 3
    assert data["score"] == 4

    mock_create_evaluation.assert_awaited_once()
    await_args = mock_create_evaluation.await_args
    assert await_args is not None

    task_id, evaluation_data, current_user, _ = await_args.args
    assert task_id == 5
    assert evaluation_data.score == 4
    assert current_user.id == 2


def test_create_evaluation_task_not_found_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    mock_create_evaluation = AsyncMock(side_effect=task_services.TaskNotFoundError())
    monkeypatch.setattr(
        evaluation_services,
        "create_evaluation",
        mock_create_evaluation,
    )

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/evaluations/tasks/5",
            json={"score": 4},
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert data["detail"] == "Task not found"

    mock_create_evaluation.assert_awaited_once()
    await_args = mock_create_evaluation.await_args
    assert await_args is not None

    task_id, evaluation_data, current_user, _ = await_args.args
    assert task_id == 5
    assert evaluation_data.score == 4
    assert current_user.id == 2


def test_create_evaluation_permission_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    mock_create_evaluation = AsyncMock(
        side_effect=evaluation_services.EvaluationPermissionError()
    )
    monkeypatch.setattr(
        evaluation_services,
        "create_evaluation",
        mock_create_evaluation,
    )

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/evaluations/tasks/5",
            json={"score": 4},
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert data["detail"] == "Not enough permissions"

    mock_create_evaluation.assert_awaited_once()
    await_args = mock_create_evaluation.await_args
    assert await_args is not None

    task_id, evaluation_data, current_user, _ = await_args.args
    assert task_id == 5
    assert evaluation_data.score == 4
    assert current_user.id == 2


def test_create_evaluation_task_not_done_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    mock_create_evaluation = AsyncMock(
        side_effect=evaluation_services.TaskNotDoneError()
    )
    monkeypatch.setattr(
        evaluation_services,
        "create_evaluation",
        mock_create_evaluation,
    )

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/evaluations/tasks/5",
            json={"score": 4},
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert data["detail"] == "Task is not done"

    mock_create_evaluation.assert_awaited_once()
    await_args = mock_create_evaluation.await_args
    assert await_args is not None

    task_id, evaluation_data, current_user, _ = await_args.args
    assert task_id == 5
    assert evaluation_data.score == 4
    assert current_user.id == 2


def test_create_evaluation_task_has_no_assignee_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    mock_create_evaluation = AsyncMock(
        side_effect=evaluation_services.TaskHasNoAssigneeError()
    )
    monkeypatch.setattr(
        evaluation_services,
        "create_evaluation",
        mock_create_evaluation,
    )

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/evaluations/tasks/5",
            json={"score": 4},
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert data["detail"] == "Task has no assignee"

    mock_create_evaluation.assert_awaited_once()
    await_args = mock_create_evaluation.await_args
    assert await_args is not None

    task_id, evaluation_data, current_user, _ = await_args.args
    assert task_id == 5
    assert evaluation_data.score == 4
    assert current_user.id == 2


def test_create_evaluation_already_exists_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    mock_create_evaluation = AsyncMock(
        side_effect=evaluation_services.EvaluationAlreadyExistsError()
    )
    monkeypatch.setattr(
        evaluation_services,
        "create_evaluation",
        mock_create_evaluation,
    )

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/evaluations/tasks/5",
            json={"score": 4},
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert data["detail"] == "Task already evaluated"

    mock_create_evaluation.assert_awaited_once()
    await_args = mock_create_evaluation.await_args
    assert await_args is not None

    task_id, evaluation_data, current_user, _ = await_args.args
    assert task_id == 5
    assert evaluation_data.score == 4
    assert current_user.id == 2


def test_get_my_evaluations_success(monkeypatch):
    evaluations = [
        Evaluation(
            id=1,
            task_id=5,
            evaluator_id=2,
            user_id=3,
            score=4,
            created_at=datetime.now(UTC),
        ),
        Evaluation(
            id=2,
            task_id=6,
            evaluator_id=2,
            user_id=3,
            score=5,
            created_at=datetime.now(UTC),
        ),
    ]

    async def fake_get_current_user():
        return User(id=3, team_id=1, role=UserRole.USER)

    mock_get_current_user_evaluations = AsyncMock(return_value=evaluations)
    monkeypatch.setattr(
        evaluation_services,
        "get_current_user_evaluations",
        mock_get_current_user_evaluations,
    )

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.get("/api/v1/evaluations/me")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["task_id"] == 5
    assert data[0]["score"] == 4
    assert data[1]["task_id"] == 6
    assert data[1]["score"] == 5

    mock_get_current_user_evaluations.assert_awaited_once()
    await_args = mock_get_current_user_evaluations.await_args
    assert await_args is not None

    current_user, _ = await_args.args
    assert current_user.id == 3


def test_get_my_average_score_success(monkeypatch):
    async def fake_get_current_user():
        return User(id=3, team_id=1, role=UserRole.USER)

    average_score = EvaluationAverageRead(
        average_score=4.5,
        evaluations_count=2,
    )

    mock_get_current_user_average_score = AsyncMock(return_value=average_score)
    monkeypatch.setattr(
        evaluation_services,
        "get_current_user_average_score",
        mock_get_current_user_average_score,
    )

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.get("/api/v1/evaluations/me/average")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert data["average_score"] == 4.5
    assert data["evaluations_count"] == 2

    mock_get_current_user_average_score.assert_awaited_once()
    await_args = mock_get_current_user_average_score.await_args
    assert await_args is not None

    current_user, _ = await_args.args
    assert current_user.id == 3
