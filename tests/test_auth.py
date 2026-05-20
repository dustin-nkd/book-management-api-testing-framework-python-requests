"""
tests/test_auth.py
------------------
Smoke tests for Authentication fixtures and /api/me endpoint.
Verifies that the session-scoped auth setup works correctly
before running the full test suite.
"""

import allure
import pytest

from config import settings
from services.auth_service import AuthService


@allure.epic("Authentication")
@allure.feature("Login")
class TestAuthFixtures:
    """Verify the auth fixtures initialize correctly"""

    @allure.story("Session token")
    @allure.title("auth_token fixture should return non-empty JWT string")
    @pytest.mark.auth
    @pytest.mark.smoke
    def test_auth_token_is_not_empty(self, auth_token: str) -> None:
        """
        Verify the session fixture successfully retrieves a JWT token.
        IF this test fails, all other authenticated tests will also fail.
        """
        assert isinstance(auth_token, str), "Token should be a string."
        assert len(auth_token) > 0, "Token should not be empty."

    @allure.story("Get current user")
    @allure.title("GET /api/me should return the authenticated user's profile")
    @pytest.mark.auth
    @pytest.mark.smoke
    def test_get_me_returns_user_profile(self, auth_service: AuthService) -> None:
        """
        Verify that /api/me returns the correct profile for the logged-in user.
        """
        response = auth_service.get_me()

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )

        body = response.json()

        # Required fields per OpenAPI spec
        for field in ["id", "name", "email"]:
            assert field in body, f"Field '{field}' misisng from /api/me response."

        assert body["email"] == settings.test_email, (
            f"Expected email '{settings.test_email}' but got '{body['email']}'"
        )

    @allure.story("Login")
    @allure.title("Login with invalid credentials should return 403 or 404")
    @pytest.mark.auth
    def test_login_with_invalid_credentials(self) -> None:
        """
        Verify that login with wrong credentials is properly rejected.
        Uses a standalone AuthService (no token) to test the raw endpoint.
        """
        auth = AuthService()
        response = auth.login(
            email="nonexistent@fake.com",
            password="wrong_password_123",
        )

        assert response.status_code in (403, 404), (
            f"Expected 403 or 404 for invalid credentials",
            f"Got {response.status_code}: {response.text}"
        )
