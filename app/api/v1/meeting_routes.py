from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.meetings import Meeting
from app.models.users import User
from app.schemas.meetings import MeetingCreate, MeetingRead
from app.services import meetings as meeting_services

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post("", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Meeting:
    try:
        return await meeting_services.create_meeting(meeting_data, current_user, db)
    except meeting_services.MeetingPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    except meeting_services.UserNotInTeamError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is not in a team",
        )
    except meeting_services.MeetingParticipantNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except meeting_services.MeetingParticipantTeamMismatchError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Participant is in other team",
        )
    except meeting_services.MeetingSelfBookingError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You cannot be participant",
        )
    except meeting_services.MeetingTimeOverlapError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Meeting time overlaps with existing meeting",
        )


@router.get("", response_model=list[MeetingRead], status_code=status.HTTP_200_OK)
async def get_my_meetings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Meeting]:
    return await meeting_services.get_current_user_meetings(current_user, db)


@router.patch(
    "/{meeting_id}/cancel", response_model=MeetingRead, status_code=status.HTTP_200_OK
)
async def cancel_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Meeting:
    try:
        return await meeting_services.cancel_meeting(meeting_id, current_user, db)
    except meeting_services.MeetingNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    except meeting_services.MeetingPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
