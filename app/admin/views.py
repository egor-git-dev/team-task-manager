from sqladmin import ModelView

from app.models.comments import Comment
from app.models.evaluations import Evaluation
from app.models.meetings import Meeting
from app.models.tasks import Task
from app.models.teams import Team
from app.models.users import User


class UserAdmin(ModelView, model=User):
    can_create = False
    column_list = [
        User.id,
        User.email,
        User.role,
        User.is_active,
        User.is_superuser,
        User.team_id,
        User.created_at,
    ]
    form_columns = [
        User.email,
        User.role,
        User.is_active,
        User.is_superuser,
        User.team_id,
    ]


class TeamAdmin(ModelView, model=Team):
    can_create = False
    column_list = [
        Team.id,
        Team.name,
        Team.join_code,
        Team.created_at,
    ]
    form_columns = [
        Team.name,
        Team.join_code,
    ]


class TaskAdmin(ModelView, model=Task):
    can_create = False
    column_list = [
        Task.id,
        Task.title,
        Task.status,
        Task.deadline,
        Task.creator_id,
        Task.assignee_id,
        Task.team_id,
        Task.created_at,
    ]
    form_columns = [
        Task.title,
        Task.description,
        Task.status,
        Task.deadline,
        Task.creator_id,
        Task.assignee_id,
        Task.team_id,
    ]


class MeetingAdmin(ModelView, model=Meeting):
    can_create = False
    column_list = [
        Meeting.id,
        Meeting.title,
        Meeting.starts_at,
        Meeting.ends_at,
        Meeting.creator_id,
        Meeting.participant_id,
        Meeting.team_id,
        Meeting.is_cancelled,
        Meeting.created_at,
    ]
    form_columns = [
        Meeting.title,
        Meeting.description,
        Meeting.starts_at,
        Meeting.ends_at,
        Meeting.creator_id,
        Meeting.participant_id,
        Meeting.team_id,
        Meeting.is_cancelled,
    ]


class EvaluationAdmin(ModelView, model=Evaluation):
    can_create = False
    column_list = [
        Evaluation.id,
        Evaluation.task_id,
        Evaluation.evaluator_id,
        Evaluation.user_id,
        Evaluation.score,
        Evaluation.created_at,
    ]
    form_columns = [
        Evaluation.task_id,
        Evaluation.evaluator_id,
        Evaluation.user_id,
        Evaluation.score,
    ]


class CommentAdmin(ModelView, model=Comment):
    can_create = False
    column_list = [
        Comment.id,
        Comment.task_id,
        Comment.author_id,
        Comment.text,
        Comment.created_at,
    ]
    form_columns = [
        Comment.task_id,
        Comment.author_id,
        Comment.text,
    ]
