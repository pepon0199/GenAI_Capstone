from types import SimpleNamespace

import pytest

from auth.service import AuthService


class FakeAuthAdmin:
    def create_user(self, payload):
        if payload["email"] == "taken@example.com":
            raise RuntimeError("User has already been registered")

        return SimpleNamespace(
            user=SimpleNamespace(
                id="user-1",
                email=payload["email"],
                user_metadata={"display_name": payload["user_metadata"]["display_name"]},
            )
        )


class FakeAuth:
    def __init__(self):
        self.admin = FakeAuthAdmin()

    def sign_in_with_password(self, payload):
        if payload["password"] != "strongpass123":
            raise RuntimeError("Invalid login credentials")

        return SimpleNamespace(
            user=SimpleNamespace(
                id="user-1",
                email=payload["email"],
                user_metadata={"display_name": "Alice"},
            )
        )


class FakeClient:
    def __init__(self):
        self.auth = FakeAuth()


def test_create_user_and_authenticate():
    service = AuthService(lambda: FakeClient())

    created_user = service.create_user("alice@example.com", "strongpass123", "Alice")
    authenticated_user = service.authenticate_user("alice@example.com", "strongpass123")

    assert created_user["email"] == "alice@example.com"
    assert authenticated_user["display_name"] == "Alice"


def test_create_user_rejects_duplicate_email():
    service = AuthService(lambda: FakeClient())

    with pytest.raises(ValueError, match="already registered"):
        service.create_user("taken@example.com", "anotherpass123", "Alice 2")


def test_authenticate_user_rejects_wrong_password():
    service = AuthService(lambda: FakeClient())

    assert service.authenticate_user("alice@example.com", "wrongpass") is None
