from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import evaluations as evaluation_crud
from app.models.evaluations import Evaluation
from app.models.tasks import TaskStatus
from app.models.users import User, UserRole
from app.schemas.evaluations import EvaluationAverageRead, EvaluationCreate
from app.services import tasks as task_services


class EvaluationPermissionError(Exception):
    pass


class TaskNotDoneError(Exception):
    pass


class TaskHasNoAssigneeError(Exception):
    pass


class EvaluationAlreadyExistsError(Exception):
    pass


async def create_evaluation(
    task_id: int,
    evaluation_data: EvaluationCreate,
    current_user: User,
    db: AsyncSession,
) -> Evaluation:
    task = await task_services.get_task_by_id_for_user_or_raise(
        task_id, current_user, db
    )
    if current_user.role not in {UserRole.MANAGER, UserRole.ADMIN}:
        raise EvaluationPermissionError()
    if task.status != TaskStatus.DONE:
        raise TaskNotDoneError()
    if task.assignee_id is None:
        raise TaskHasNoAssigneeError()
    existing_evaluation = await evaluation_crud.get_evaluation_by_task_id(task.id, db)
    if existing_evaluation is not None:
        raise EvaluationAlreadyExistsError()

    return await evaluation_crud.create_evaluation(
        task.id,
        current_user.id,
        task.assignee_id,
        evaluation_data,
        db,
    )


async def get_current_user_evaluations(
    current_user: User,
    db: AsyncSession,
) -> list[Evaluation]:
    return await evaluation_crud.get_user_evaluations(current_user.id, db)


async def get_current_user_average_score(
    current_user: User,
    db: AsyncSession,
) -> EvaluationAverageRead:
    average_score = await evaluation_crud.get_user_average_score(current_user.id, db)
    evaluations_count = await evaluation_crud.get_user_evaluations_count(
        current_user.id, db
    )
    return EvaluationAverageRead(
        average_score=average_score,
        evaluations_count=evaluations_count,
    )
