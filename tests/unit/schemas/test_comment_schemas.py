import pytest
from pydantic import ValidationError

from app.schemas.comments import CommentCreate


def test_valid_comment():
    comment = CommentCreate(text="valid comment")
    assert comment.text == "valid comment"


def test_empty_string_comment():
    with pytest.raises(ValidationError):
        CommentCreate(text="")


def test_too_long_comment():
    with pytest.raises(ValidationError):
        CommentCreate(text="".join(["a" for _ in range(1001)]))
