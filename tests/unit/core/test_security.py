from jose import jwt

from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings


def test_password_hashing_and_verification():
    password = "test_password"
    hashed_password = get_password_hash(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("wrong-password", hashed_password)


def test_create_access_token():
    token = create_access_token(subject=str(1))
    payload = jwt.decode(
        token,
        key=settings.secret_key,
        algorithms=[settings.algorithm],
    )

    assert isinstance(token, str)
    assert payload["sub"] == "1"
    assert "exp" in payload
