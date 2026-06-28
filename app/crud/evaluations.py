from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluations import Evaluation
from app.schemas.evaluations import EvaluationCreate


async def create_evaluation(
    task_id: int,
    evaluator_id: int,
    user_id: int,
    evaluation_data: EvaluationCreate,
    db: AsyncSession,
) -> Evaluation:
    evaluation = Evaluation(
        task_id=task_id,
        evaluator_id=evaluator_id,
        user_id=user_id,
        score=evaluation_data.score,
    )
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    return evaluation


async def get_evaluation_by_task_id(
    task_id: int, db: AsyncSession
) -> Evaluation | None:
    query = select(Evaluation).where(Evaluation.task_id == task_id)
    result = await db.execute(query)

    return result.scalar_one_or_none()


async def get_user_evaluations(user_id: int, db: AsyncSession) -> list[Evaluation]:
    query = (
        select(Evaluation)
        .where(Evaluation.user_id == user_id)
        .order_by(Evaluation.created_at.desc())
    )
    result = await db.execute(query)

    return list(result.scalars().all())


async def get_user_average_score(user_id: int, db: AsyncSession) -> float | None:
    query = select(func.avg(Evaluation.score)).where(Evaluation.user_id == user_id)
    result = await db.execute(query)

    average_score = result.scalar_one_or_none()

    return float(average_score) if average_score is not None else None


async def get_user_evaluations_count(user_id: int, db: AsyncSession) -> int:
    query = select(func.count(Evaluation.id)).where(Evaluation.user_id == user_id)
    result = await db.execute(query)

    return result.scalar_one()
