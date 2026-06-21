import pytest
from pydantic import ValidationError

from app.schemas.users import UserCreate


def test_valid_email():
    user = UserCreate(email="example@example.com", password="12345678")
    assert user.email == "example@example.com"


def test_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(email="bad_email", password="12345678")


def test_short_password():
    with pytest.raises(ValidationError):
        UserCreate(email="example@example.com", password="12345")
