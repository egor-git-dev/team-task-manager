from app.core.config import settings


def test_database_url():
    assert (
        settings.database_url
        == "postgresql+asyncpg://postgres:postgres@localhost:5432/team_task_manager"
    )


def test_sync_database_url():
    assert (
        settings.sync_database_url
        == "postgresql+psycopg://postgres:postgres@localhost:5432/team_task_manager"
    )
