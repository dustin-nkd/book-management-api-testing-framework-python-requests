"""
tests/test_auth.py
------------------
Automation test script for Authentication Management endpoints.
"""

import allure
import pytest

from config import settings
from data.auth_data import (
    LOGIN_MISSING_FIELD_CASES,
    REGISTRATION_MISSING_FIELD_CASES,
    UPDATE_PROFILE_NEW_NAME,
    UPDATE_PROFILE_NEW_PASSWORD,
    unique_register_email,
)
from services.auth_service import AuthService


@allure.epic("Authentication")
class TestAuthFixtures:
    """TC-AUTH-01: Smoke test - verify session  fixture initializes correctly."""

    @allure.feature("Login")
    @allure.story("Session token")
    @allure.title("TC-AUTH-01: auth_token fixture should return a non-empty JWT string")
    @pytest.mark.auth
    @pytest.mark.smoke
    def test_auth_token_is_not_empty(self, auth_token: str) -> None:
        """
        Verify the session fixture successfully retrieves a JWT access token.
        If this test fails, all other authenticated tests will also fail -
        check login credentials and server availability first.
        """
        assert isinstance(auth_token, str), "Token should be a string."
        assert len(auth_token) > 0, "Token should not be empty."


@allure.epic("Authentication")
class TestLogin:
    """TC-AUTH-02 to TC-AUTH-06: POST /api/login"""

    @allure.epic("Login")
    @allure.story("Wrong password")
    @allure.title("TC-AUTH-02: Login with correct email but wrong password should return 400")
    @pytest.mark.auth
    def test_login_wrong_password(self) -> None:
        """
        Verify that login with a correct email but wrong password is rejected.
        Server returns 400 (not 403) with a 'fields.password' error object.
        """
        auth = AuthService()
        response = auth.login(
            email=settings.test_email,
            password="wrong_password_999",
        )

        assert response.status_code == 400, (
            f"Expected 400 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Invalid password."
        assert "fields" in body
        assert "password" in body["fields"]

    @allure.feature("Login")
    @allure.story("Unregistered email")
    @allure.title("TC-AUTH-03: Login with unregistered email should return 404")
    @pytest.mark.auth
    def test_login_unregistered_email(self) -> None:
        """
        Verify that login with a non-existent email returns 404
        with a 'fields.email' error pointing the user to register.
        """
        auth = AuthService()
        response = auth.login(
            email="nonexistent_autotest@fake.com",
            password="any_password",
        )

        assert response.status_code == 404, (
            f"Expected 404 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "User not found."
        assert "fields" in body
        assert "email" in body["fields"]

    @allure.feature("Login")
    @allure.story("Validation error - missing required field")
    @allure.title("TC-AUTH-04/05: Login with missing required field should return 422")
    @pytest.mark.auth
    @pytest.mark.parametrize(
        "case_id, payload, expected_status, expected_field",
        LOGIN_MISSING_FIELD_CASES,
        ids=[c[0] for c in LOGIN_MISSING_FIELD_CASES],
    )
    def test_login_missing_field(
            self,
            case_id: str,
            payload: dict,
            expected_status: int,
            expected_field: str,
    ) -> None:
        """
        Verify that omitting a required login field (email or password)
        triggers a 422 validation error with a per-field error object.
        Server validates fields independently - only the missing field appears in 'fields'.
        """
        auth = AuthService()
        response = auth.post("/api/login", payload=payload)

        assert response.status_code == expected_status, (
            f"[{case_id}] Expected {expected_status} "
            f"but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Invalid data."
        assert "fields" in body, "Expected 'fields' key in 422 response body."
        assert expected_field in body["fields"], (
            f"[{case_id}] Expected '{expected_field}' in fields "
            f"but got {body['fields']}"
        )

    @allure.feature("Login")
    @allure.story("Validation error - invalid email format")
    @allure.title("TC-AUTH-06: Login with invalid email format should return 422")
    @pytest.mark.auth
    def test_login_invalid_email_format(self) -> None:
        """
        Verify that a malformed email string is rejected at the validation layer
        with a format-specific error (not the 'found: undefined' missing-field error).
        """
        auth = AuthService()
        response = auth.login(
            email="not-an-email",
            password="some_password",
        )

        assert response.status_code == 422, (
            f"Expected 422 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Invalid data."
        assert "fields" in body
        assert "email" in body["fields"]
        assert body["fields"]["email"] == ["Property 'email' should be email"], (
            f"Expected format-specific error but got: {body['fields']['email']}"
        )


@allure.epic("Authentication")
class TestRegister:
    """TC-AUTH-07 to TC-AUTH-13: POST /api/register"""

    @allure.feature("Register")
    @allure.story("Valid registration - full payload")
    @allure.title("TC-AUTH-07: Register with all fields should return 201")
    @pytest.mark.auth
    def test_register_valid_full_payload(self) -> None:
        """
        Verify a new account can be registered with all available fields.
        Note: registered accounts persist in the DB - there is no DELETE /api/user.
        """
        auth = AuthService()
        response = auth.register(
            name="AutoTest User",
            email=unique_register_email("autotest_full"),
            password="Test@12345",
            phone="0901234567",
            address="123 AutoTest Street",
        )

        assert response.status_code == 201, (
            f"Expected 201 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Register successfully."

    @allure.feature("Register")
    @allure.story("Valid registration - required fields only")
    @allure.title("TC-AUTH-08: Register with required fields only should return 201")
    @pytest.mark.auth
    def test_register_required_fields_only(self) -> None:
        """
        Verify that phone, address, and avatarUrl are truly optional -
        omitting them does not cause validation errors.
        """
        auth = AuthService()
        response = auth.register(
            name="AutoTest Minimal",
            email=unique_register_email("autotest_min"),
            password="Test@12345",
        )

        assert response.status_code == 201, (
            f"Expected 201 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Register successfully."

    @allure.feature("Register")
    @allure.story("Duplicate email")
    @allure.title("TC-AUTH-09: Register with duplicate email should return 422")
    @pytest.mark.auth
    def test_register_duplicate_email(self) -> None:
        """
        Verify that registering with an already-existing email is rejected.
        Note: server returns 422 (not 400) for duplicate email - inconsistent
        with the category duplicate pattern (TC-CAT-03) which causes 400.
        """
        auth = AuthService()
        response = auth.register(
            name="Duplicate user",
            email=settings.test_email,
            password="Test@12345",
        )

        assert response.status_code == 422, (
            f"Expected 422 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Email already exists."
        assert 'fields' in body
        assert "email" in body["fields"]

    @allure.feature("Register")
    @allure.story("Validation error - missing required fields")
    @allure.title("TC-AUTH-10/11/12: Register with missing required fields should return 422")
    @pytest.mark.auth
    @pytest.mark.parametrize(
        "case_id, payload, expected_status, expected_field",
        REGISTRATION_MISSING_FIELD_CASES,
        ids=[c[0] for c in REGISTRATION_MISSING_FIELD_CASES],
    )
    def test_register_missing_field(
            self,
            case_id: str,
            payload: dict,
            expected_status: int,
            expected_field: str,
    ) -> None:
        """
        Verify that omitting any required registration field (name, email, or password)
        triggers a 422 response with per-field error object.
        Server validates independently - only the missing field appears in 'fields'.
        """
        auth = AuthService()
        response = auth.post("/api/register", payload=payload)

        assert response.status_code == expected_status, (
            f"[{case_id}] Expected {expected_status} "
            f"but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Invalid data."
        assert 'fields' in body, "Expected 'fields' key in 422 response body."
        assert expected_field in body["fields"], (
            f"[{case_id}] Expected '{expected_field}' in fields "
            f"but got {body['fields']}"
        )

    @allure.feature("Register")
    @allure.story("Validation error - invalid email format")
    @allure.title("TC-AUTH-13: Register with invalid email format should return 422")
    @pytest.mark.auth
    def test_register_invalid_email_format(self) -> None:
        """
        Verify that a malformed email string is rejected with the same format-specific
        error as TC-AUTH-06 - email format validation is consistent across endpoints.
        """
        auth = AuthService()
        response = auth.register(
            name="AutoTest User",
            email="not-an-email",
            password="Test@12345",
        )

        assert response.status_code == 422, (
            f"Expected 422 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Invalid data."
        assert 'fields' in body
        assert "email" in body["fields"]
        assert body["fields"]["email"] == ["Property 'email' should be email"], (
            f"Expected format-specific error but got {body['fields']['email']}"
        )


@allure.epic("Authentication")
class TestGetMe:
    """TC-AUTH-14 to TC-AUTH:15: GET /api/me"""

    @allure.feature("Get me")
    @allure.story("Authenticated")
    @allure.title("TC-AUTH-14: GET /api/me with valid token should return full user profile")
    @pytest.mark.auth
    @pytest.mark.smoke
    def test_get_me_authenticated(self, auth_service: AuthService) -> None:
        """
        Verify /api/me returns the complete profile for the authenticated user.
        Response is a flat user object - no 'msg' field.
        Includes the undocumented 'config' field confirmed during manual testing.
        """
        response = auth_service.get_me()

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )

        body = response.json()

        # All fields present in confirm actual response (TC-AUTH-14)
        for field in ["id", "name", "email", "avatarUrl", "phone", "address", "config"]:
            assert field in body, f"Field '{field}' missing from /api/me response."

        # Type assertions
        assert isinstance(body["id"], str) and body["id"], "'id' must be a non-empty string."
        assert isinstance(body["name"], str), "'name' must be a string."
        assert isinstance(body["email"], str), "'email' must be a string."
        assert isinstance(body["avatarUrl"], str), "'avatarUrl' must be a string (not null)."
        assert isinstance(body["config"], dict), "'config' must be an object."

        # Email must match the test account
        assert body["email"] == settings.test_email, (
            f"Expected email '{settings.test_email}' but got '{body['email']}'"
        )

    @allure.feature("Get Me")
    @allure.story("Unauthenticated")
    @allure.title("TC-AUTH-15: GET /api/me without token should return 401")
    @pytest.mark.auth
    def test_get_me_no_token(self) -> None:
        """
        Verify that /api/me returns 401 when no Authorization header is provided.
        """
        auth = AuthService()  # No token set
        response = auth.get_me()

        assert response.status_code == 401, (
            f"Expected 401 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Missing or invalid Authorization header"


@allure.epic("Authentication")
class TestUpdateProfile:
    """TC-AUTH-16 to TC-AUTH-19: PATCH /api/profile"""

    @allure.feature("Update Profile")
    @allure.story("Valid name change")
    @allure.title("TC-AUTH-16: Update profile name with valid token should return 200")
    @pytest.mark.auth
    def test_update_profile_valid_name(self, auth_service: AuthService) -> None:
        """
        Verify that the authenticated user's name can be updated successfully.
        Fetches the original name from GET /api/me before updating and
        restores it in teardown regardless of test outcome.
        """
        original_name = auth_service.get_me().json().get("name", "")

        try:
            response = auth_service.update_profile({"name": UPDATE_PROFILE_NEW_NAME})

            assert response.status_code == 200, (
                f"Expected 200 but got {response.status_code}: {response.text}"
            )
            assert response.json().get("msg") == "Updated profile successfully."
        finally:
            auth_service.update_profile({"name": original_name})

    @allure.feature("Update Profile")
    @allure.story("Change password - correct old password")
    @allure.title("TC-AUTH-17: Change password with correct password_old should return 200")
    @pytest.mark.auth
    def test_update_profile_change_password(self, auth_service: AuthService) -> None:
        """
        Verify that the authenticated user can change their password when
        the correct current password is provided (flat payload format).
        Restores the original password in teardown.

        Note: flat payload format validates 'password_old' correctly.
        The 'fields' wrapper format does NOT validate 'password_old' (see TC-AUTH-18).
        """
        password_changed = False

        try:
            response = auth_service.update_profile({
                "password": UPDATE_PROFILE_NEW_PASSWORD,
                "password_old": settings.test_password,
            })

            if response.status_code == 200:
                password_changed = True

            assert response.status_code == 200, (
                f"Expected 200 but got {response.status_code}: {response.text}"
            )
            assert response.json().get("msg") == "Updated profile successfully."
        finally:
            if password_changed:
                # Restore original password — use flat format (validates password_old correctly)
                auth_service.update_profile({
                    "password": settings.test_password,
                    "password_old": UPDATE_PROFILE_NEW_PASSWORD,
                })

    @allure.feature("Update Profile")
    @allure.story("Change password - wrong old password")
    @allure.title("TC-AUTH-18: Change password with wrong password_old should return 400/403 — BUG")
    @pytest.mark.auth
    @pytest.mark.xfail(
        reason=(
                "BUG: PATCH /api/profile with 'fields' wrapper payload does not validate "
                "'password_old' — server returns 200 and changes the password regardless, "
                "instead of 400/403. Security vulnerability: any authenticated user can "
                "change their password without knowing the current one."
        ),
        strict=False,
    )
    def test_update_profile_wrong_old_password(self, auth_service: AuthService) -> None:
        """
        Verify that providing an incorrect 'password_old' rejects the password change.

        Currently marked xfail due to a security bug:
        The 'fields' wrapper format bypasses 'password_old' validation entirely —
        server returns 200 and changes the password regardless.

        Expected: 400 or 403. Actual: 200 (password changed).
        If this test starts passing in the future, the bug has been fixed.
        """
        password_changed = False

        try:
            response = auth_service.update_profile({
                "fields": {
                    "password": UPDATE_PROFILE_NEW_PASSWORD,
                    "password_old": "wrong_old_password",
                }
            })

            if response.status_code == 200:
                password_changed = True

            assert response.status_code in (400, 403), (
                f"Expected 400/403 for wrong password_old "
                f"but got {response.status_code}: {response.text}\n"
                "Security vulnerability: 'fields' wrapper bypasses password_old validation."
            )
        finally:
            if password_changed:
                allure.attach(
                    body=(
                        "BUG: PATCH /api/profile with 'fields' wrapper does not validate "
                        "'password_old'.\n"
                        "Any authenticated user can change their password without knowing "
                        "the current one.\nExpected: 400/403. Actual: 200."
                    ),
                    name="⚠️ Security Bug — password_old not validated",
                    attachment_type=allure.attachment_type.TEXT,
                )
                # Restore using 'fields' wrapper — this also bypasses password_old (due to bug)
                auth_service.update_profile({
                    "fields": {
                        "password": settings.test_password,
                        "password_old": UPDATE_PROFILE_NEW_PASSWORD,
                    }
                })

    @allure.feature("Update Profile")
    @allure.story("Unauthenticated")
    @allure.title("TC-AUTH-19: PATCH /api/profile without token should return 401")
    @pytest.mark.auth
    def test_update_profile_no_token(self) -> None:
        """
        Verify that PATCH /api/profile returns 401 when no Authorization header is provided.
        """
        auth = AuthService()  # No token set
        response = auth.update_profile({"name": "Unauthorized Attempt"})

        assert response.status_code == 401, (
            f"Expected 401 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Missing or invalid Authorization header"


@allure.epic("Authentication")
class TestLogout:
    """TC-AUTH-20 to TC-AUTH-21: DELETE /api/logout"""

    @allure.feature("Logout")
    @allure.story("Authenticated")
    @allure.title("TC-AUTH-20: Logout with valid token should return 200")
    @pytest.mark.auth
    def test_logout_authenticated(self, fresh_login_service: AuthService) -> None:
        """
        Verify that the logout endpoint invalidates a valid session.
        Uses an isolated fresh token from fresh_login_service — NOT the shared
        session token — to avoid breaking authentication for the rest of the suite.
        """
        response = fresh_login_service.logout()

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Logout successfully."

    @allure.feature("Logout")
    @allure.story("Unauthenticated")
    @allure.title("TC-AUTH-21: DELETE /api/logout without token should return 401 with empty body")
    @pytest.mark.auth
    def test_logout_no_token(self) -> None:
        """
        Verify that DELETE /api/logout returns 401 when no token is provided.
        Note: unlike GET /api/me and PATCH /api/profile (which return a 'msg' on 401),
        this endpoint returns an empty object {} — behavior is inconsistent across
        protected endpoints and matters for automation assertions.
        """
        auth = AuthService()  # No token set
        response = auth.logout()

        assert response.status_code == 401, (
            f"Expected 401 but got {response.status_code}: {response.text}"
        )
        assert response.json() == {}, (
            f"Expected empty body {{}} but got: {response.json()}"
        )


@allure.epic("Authentication")
class TestRefetchToken:
    """TC-AUTH-22 to TC-AUTH-23: POST /api/refetch-token"""

    @allure.feature("Refetch Token")
    @allure.story("Valid cookie")
    @allure.title("TC-AUTH-22: Refetch token with valid refetchToken cookie should return 200")
    @pytest.mark.auth
    def test_refetch_token_valid_cookie(self, fresh_login_service: AuthService) -> None:
        """
        Verify that POST /api/refetch-token returns a new JWT when the refetchToken
        cookie is present. The fresh_login_service fixture provides a session where
        this cookie was set by the server at login time.

        Response schema is identical to POST /api/login: {msg, accessToken, exp}.
        """
        response = fresh_login_service.refetch_token()

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Refetch token successfully."
        assert "accessToken" in body
        assert isinstance(body["accessToken"], str) and body["accessToken"], (
            "'accessToken' must be a non-empty string."
        )
        assert body.get("exp") == "6d", (
            f"Expected exp='6d' but got: {body.get('exp')}"
        )

    @allure.feature("Refetch Token")
    @allure.story("No cookie")
    @allure.title("TC-AUTH-23: Refetch token without cookie should return 422")
    @pytest.mark.auth
    def test_refetch_token_no_cookie(self) -> None:
        """
        Verify that POST /api/refetch-token returns 422 when the required
        refetchToken cookie is absent from the request.
        """
        auth = AuthService()  # Fresh service with no login — no refetchToken cookie
        response = auth.refetch_token()

        assert response.status_code == 422, (
            f"Expected 422 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Invalid data."
        assert "fields" in body
        assert "refetchToken" in body["fields"], (
            f"Expected 'refetchToken' in fields but got: {body['fields']}"
        )
