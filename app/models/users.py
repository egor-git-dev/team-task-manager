from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.comments import Comment
    from app.models.tasks import Task
    from app.models.teams import Team


class UserRole(str, Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=UserRole.USER,
        nullable=False,
    )
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    created_tasks: Mapped[list["Task"]] = relationship(
        back_populates="creator",
        foreign_keys="Task.creator_id",
    )

    assigned_tasks: Mapped[list["Task"]] = relationship(
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )
    team: Mapped["Team | None"] = relationship(back_populates="users")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author")
