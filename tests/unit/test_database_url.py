from app.core.config import settings


def test_database_url():
    assert (
        settings.database_url
        == "postgresql+asyncpg://postgres:postgres@localhost:5432/team_task_manager"
    )
