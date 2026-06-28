from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.evaluations import Evaluation
from app.models.users import User
from app.schemas.evaluations import (
    EvaluationAverageRead,
    EvaluationCreate,
    EvaluationRead,
)
from app.services import evaluations as evaluation_services
from app.services import tasks as task_services

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.post(
    "/tasks/{task_id}",
    response_model=EvaluationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_evaluation(
    task_id: int,
    evaluation_data: EvaluationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Evaluation:
    try:
        return await evaluation_services.create_evaluation(
            task_id, evaluation_data, current_user, db
        )
    except task_services.TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    except evaluation_services.EvaluationPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    except evaluation_services.TaskNotDoneError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task is not done",
        )
    except evaluation_services.TaskHasNoAssigneeError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task has no assignee",
        )
    except evaluation_services.EvaluationAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task already evaluated",
        )


@router.get("/me", response_model=list[EvaluationRead], status_code=status.HTTP_200_OK)
async def get_my_evaluations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Evaluation]:
    return await evaluation_services.get_current_user_evaluations(current_user, db)


@router.get(
    "/me/average", response_model=EvaluationAverageRead, status_code=status.HTTP_200_OK
)
async def get_my_average_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EvaluationAverageRead:
    return await evaluation_services.get_current_user_average_score(current_user, db)
