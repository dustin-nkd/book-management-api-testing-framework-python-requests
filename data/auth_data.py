"""
data/auth_data.py
-----------------
Centralized test data for Authentication Management tests.
"""

import time

from config import settings


# ---------------------------------------------------------------------------
# Unique email generator
# Using timestamp suffix to avoid conflicts in the shared test environment.
# Note: there is no DELETE /api/user endpoint — registered accounts persist.
# ---------------------------------------------------------------------------

def unique_register_email(prefix: str = "autotest") -> str:
    """
    Generate a unique email address using a timestamp suffix.
    Prevents naming conflicts when running tests against a shared environment.

    Args:
        prefix: Human-readable prefix to identify the account in the DB.

    Returns:
        A unique email string in the format: "{prefix}_{timestamp}@test.com"
    """
    return f"{prefix}_{int(time.time())}@test.com"


# ---------------------------------------------------------------------------
# Parametrize data: POST /api/login — missing required fields
# Used in: test_auth.py::TestLogin::test_login_missing_field
# TC-AUTH-04: missing email | TC-AUTH-05: missing password
# ---------------------------------------------------------------------------

LOGIN_MISSING_FIELD_CASES = [
    (
        "missing_email_field",          # TC-AUTH-04 - test case ID shown in Allure/terminal
        {"password": "some_password"},  # Payload with email omitted
        422,                            # Expected status code
        "email",                        # Expected field key in 'fields' error object
    ),
    (
        "missing_password_field",       # TC-AUTH-05
        {"email": settings.test_email},  # Payload with password omitted
        422,
        "password",
    )
]

# ---------------------------------------------------------------------------
# Parametrize data: POST /api/register — missing required fields
# Used in: test_auth.py::TestRegister::test_register_missing_field
# TC-AUTH-10: missing name | TC-AUTH-11: missing email | TC-AUTH-12: missing password
# ---------------------------------------------------------------------------

REGISTRATION_MISSING_FIELD_CASES = [
    (
        "missing_name_field",                                               # TC-AUTH-10
        {"email": "autotest_fixture@test.com", "password": "Test@12345"},   # name omitted
        422,
        "name",
    ),
    (
        "missing_email_field",                                              # TC-AUTH-11
        {"name": "AutoTest User", "password": "Test@12345"},                # email omitted
        422,
        "email",
    ),
    (
        "missing_password_field",                                           # TC-AUTH-12
        {"name": "AutoTest User", "email": "autotest_fixture@test.com"},    # password omitted
        422,
        "password",
    ),
]

# ---------------------------------------------------------------------------
# Update profile: field values for TC-AUTH-16, TC-AUTH-17, TC-AUTH-18
# ---------------------------------------------------------------------------

# New name used in TC-AUTH-16 (restored to original in test teardown)
UPDATE_PROFILE_NEW_NAME = "AutoTest Updated Name"

# New password used in TC-AUTH-17 and TC-AUTH-18 (restored in teardown)
UPDATE_PROFILE_NEW_PASSWORD = "NewTest@9999"
