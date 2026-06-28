from datetime import UTC, datetime

import pytest

from app.crud import evaluations as evaluation_crud
from app.models.tasks import Task
from app.models.teams import Team
from app.models.users import User
from app.schemas.evaluations import EvaluationCreate


@pytest.mark.asyncio
async def test_create_evaluation(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    user = User(email="1@example.com", hashed_password="hashed", team=team)
    evaluator = User(email="evaluator@example.com", hashed_password="hashed", team=team)
    async_session.add_all([user, team, evaluator])
    await async_session.commit()
    await async_session.refresh(user)
    task = Task(
        title="Task 1",
        description="Description 1",
        creator_id=evaluator.id,
        assignee_id=user.id,
        team_id=team.id,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    evaluation_data = EvaluationCreate(score=4)

    evaluation = await evaluation_crud.create_evaluation(
        task.id,
        evaluator.id,
        user.id,
        evaluation_data,
        async_session,
    )

    assert evaluation.score == 4
    assert evaluation.evaluator_id == evaluator.id
    assert evaluation.user_id == user.id
    assert evaluation.task_id == task.id


@pytest.mark.asyncio
async def test_get_evaluation_by_task_id(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    user = User(email="1@example.com", hashed_password="hashed", team=team)
    evaluator = User(email="evaluator@example.com", hashed_password="hashed", team=team)
    async_session.add_all([user, team, evaluator])
    await async_session.commit()
    await async_session.refresh(user)
    task = Task(
        title="Task 1",
        description="Description 1",
        creator_id=evaluator.id,
        assignee_id=user.id,
        team_id=team.id,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    evaluation_data = EvaluationCreate(score=4)
    created_evaluation = await evaluation_crud.create_evaluation(
        task.id,
        evaluator.id,
        user.id,
        evaluation_data,
        async_session,
    )

    evaluation = await evaluation_crud.get_evaluation_by_task_id(task.id, async_session)

    assert evaluation is not None
    assert evaluation.id == created_evaluation.id
    assert evaluation.score == 4


@pytest.mark.asyncio
async def test_get_user_evaluations(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    user_1 = User(email="1@example.com", hashed_password="hashed", team=team)
    user_2 = User(email="2@example.com", hashed_password="hashed", team=team)
    evaluator = User(email="evaluator@example.com", hashed_password="hashed", team=team)
    async_session.add_all([user_1, user_2, team, evaluator])
    await async_session.commit()
    task_1 = Task(
        title="Task 1",
        description="Description 1",
        creator_id=evaluator.id,
        assignee_id=user_1.id,
        team_id=team.id,
    )
    task_2 = Task(
        title="Task 2",
        description="Description 2",
        creator_id=evaluator.id,
        assignee_id=user_1.id,
        team_id=team.id,
    )
    task_3 = Task(
        title="Task 3",
        description="Description 3",
        creator_id=evaluator.id,
        assignee_id=user_2.id,
        team_id=team.id,
    )
    async_session.add_all([task_1, task_2, task_3])
    await async_session.commit()
    evaluation_data_1 = EvaluationCreate(score=4)
    evaluation_data_2 = EvaluationCreate(score=5)
    evaluation_data_3 = EvaluationCreate(score=3)
    evaluation_1 = await evaluation_crud.create_evaluation(
        task_1.id,
        evaluator.id,
        user_1.id,
        evaluation_data_1,
        async_session,
    )
    evaluation_2 = await evaluation_crud.create_evaluation(
        task_2.id,
        evaluator.id,
        user_1.id,
        evaluation_data_2,
        async_session,
    )
    evaluation_3 = await evaluation_crud.create_evaluation(
        task_3.id,
        evaluator.id,
        user_2.id,
        evaluation_data_3,
        async_session,
    )
    evaluations = await evaluation_crud.get_user_evaluations(user_1.id, async_session)
    evaluations_scores = {evaluation.score for evaluation in evaluations}

    assert len(evaluations) == 2
    assert {evaluation.user_id for evaluation in evaluations} == {user_1.id}
    assert evaluations_scores == {4, 5}


@pytest.mark.asyncio
async def test_get_user_average_score(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    user = User(email="1@example.com", hashed_password="hashed", team=team)
    evaluator = User(email="evaluator@example.com", hashed_password="hashed", team=team)
    async_session.add_all([team, user, evaluator])
    await async_session.commit()

    task_1 = Task(
        title="Task 1",
        description="Description 1",
        creator_id=evaluator.id,
        assignee_id=user.id,
        team_id=team.id,
    )
    task_2 = Task(
        title="Task 2",
        description="Description 2",
        creator_id=evaluator.id,
        assignee_id=user.id,
        team_id=team.id,
    )
    async_session.add_all([task_1, task_2])
    await async_session.commit()

    await evaluation_crud.create_evaluation(
        task_1.id,
        evaluator.id,
        user.id,
        EvaluationCreate(score=4),
        async_session,
    )
    await evaluation_crud.create_evaluation(
        task_2.id,
        evaluator.id,
        user.id,
        EvaluationCreate(score=5),
        async_session,
    )

    average_score = await evaluation_crud.get_user_average_score(
        user.id,
        async_session,
    )

    assert average_score == 4.5


@pytest.mark.asyncio
async def test_get_user_evaluations_count(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    user = User(email="1@example.com", hashed_password="hashed", team=team)
    other_user = User(email="2@example.com", hashed_password="hashed", team=team)
    evaluator = User(email="evaluator@example.com", hashed_password="hashed", team=team)
    async_session.add_all([team, user, other_user, evaluator])
    await async_session.commit()

    task_1 = Task(
        title="Task 1",
        description="Description 1",
        creator_id=evaluator.id,
        assignee_id=user.id,
        team_id=team.id,
    )
    task_2 = Task(
        title="Task 2",
        description="Description 2",
        creator_id=evaluator.id,
        assignee_id=user.id,
        team_id=team.id,
    )
    task_3 = Task(
        title="Task 3",
        description="Description 3",
        creator_id=evaluator.id,
        assignee_id=other_user.id,
        team_id=team.id,
    )
    async_session.add_all([task_1, task_2, task_3])
    await async_session.commit()

    await evaluation_crud.create_evaluation(
        task_1.id,
        evaluator.id,
        user.id,
        EvaluationCreate(score=4),
        async_session,
    )
    await evaluation_crud.create_evaluation(
        task_2.id,
        evaluator.id,
        user.id,
        EvaluationCreate(score=5),
        async_session,
    )
    await evaluation_crud.create_evaluation(
        task_3.id,
        evaluator.id,
        other_user.id,
        EvaluationCreate(score=3),
        async_session,
    )

    evaluations_count = await evaluation_crud.get_user_evaluations_count(
        user.id,
        async_session,
    )

    assert evaluations_count == 2


@pytest.mark.asyncio
async def test_get_user_average_score_and_count_without_evaluations(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    user = User(email="1@example.com", hashed_password="hashed", team=team)

    async_session.add_all([team, user])
    await async_session.commit()

    average_score = await evaluation_crud.get_user_average_score(
        user.id,
        async_session,
    )
    evaluations_count = await evaluation_crud.get_user_evaluations_count(
        user.id,
        async_session,
    )

    assert average_score is None
    assert evaluations_count == 0
