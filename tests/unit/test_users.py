import pytest
from pydantic import ValidationError

from app.models.users import UserRole
from app.schemas.users import UserCreate


def test_user_roles():
    assert {role.value for role in UserRole} == {"user", "manager", "admin"}


def test_valid_email():
    user = UserCreate(email="example@example.com", password="12345678")
    assert user.email == "example@example.com"


def test_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(email="bad_email", password="12345678")


def test_short_password():
    with pytest.raises(ValidationError):
        UserCreate(email="example@example.com", password="12345")
