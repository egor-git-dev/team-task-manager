from app.models.users import UserRole


def test_user_roles():
    assert {role.value for role in UserRole} == {"user", "manager", "admin"}
