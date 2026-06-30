"""
tests/conftest.py
----------------
Pytest fixtures shared across all test modules.

Fixture scopes used:
    session  - Created once per entire test run (login, service instances).
    function - Created and torn down for each individual test (e.g. created_book_id).
"""

import allure
import pytest

from config import settings
from data.category_data import unique_category_name
from services.auth_service import AuthService
from services.book_service import BookService
from services.category_service import CategoryService
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Authentication fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def auth_token() -> str:
    """
    Perform login once per test session and return the JWT access token.

    Scope: session - login is called exactly once regardless of how many
    tests need authentication. This avoids redundant login requests and
    prevents potential rate-limiting from the server.

    Returns:
        JWT access token string.

    Raises:
        AssertionError: If login fails or token is absent in the response.
    """
    logger.info("Session setup: authenticating as %s", settings.test_email)

    auth = AuthService()
    response = auth.login(
        email=settings.test_email,
        password=settings.test_password,
    )

    assert response.status_code == 200, (
        f"Login failed during session setup.\n"
        f"Status: {response.status_code}\n"
        f"Body:   {response.text}"
    )

    token = response.json().get("accessToken", "")
    assert token, "Login succeeded (HTTP 200) but 'accessToken' is missing in response."

    logger.info("Session setup: token acquired successfully.")
    return token


# ---------------------------------------------------------------------------
# Service fixtures — pre-authenticated instances ready to use in tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def auth_service(auth_token: str) -> AuthService:
    """
    Provide a session-scoped AuthService instance with token pre-injected.
    Used for tests that call /api/me, /api/profile, /api/logout.

    Args:
        auth_token: JWT token from the auth_token fixture.

    Returns:
        AuthService instance with Authorization header set.
    """
    service = AuthService()
    service.set_token(auth_token)
    return service


@pytest.fixture(scope="session")
def book_service(auth_token: str) -> BookService:
    """
    Provide a session-scoped BookService instance with token pre-injected.
    Used for all book-related tests requiring authentication.

    Args:
        auth_token: JWT token from the auth_token fixture.

    Returns:
        BookService instance with Authorization header set.
    """
    service = BookService()
    service.set_token(auth_token)
    return service


@pytest.fixture(scope="session")
def category_service(auth_token: str) -> CategoryService:
    """
    Provide a session-scoped CategoryService instance with token pre-injected.
    Used for all category-related tests requiring authentication.

    Args:
        auth_token: JWT token from the auth_token fixture.

    Returns:
        CategoryService instance with Authorization header set.
    """
    service = CategoryService()
    service.set_token(auth_token)
    return service


@pytest.fixture(scope="session")
def public_book_service() -> BookService:
    """
    Provide a session-scoped BookService instance WITHOUT authentication.
    Used for tests targeting public endpoints (e.g. GET /api/book).

    Returns:
        BookService instance with no Authorization header.
    """
    return BookService()


@pytest.fixture(scope="function")
def fresh_login_service() -> AuthService:
    """
    Create a fresh AuthService with its own isolated login session.

    Used for tests that consume or invalidate the token (logout) or require
    the refetchToken cookie (refetch-token), where reusing the shared session
    token would break authentication for other tests in the suite.

    Scope: function - each test gets its own independent session with a
    separate token and separate cookie jar from the main auth_token fixture.

    Returns:
        AuthService with a fresh token and session cookies set.
    """
    logger.info("fresh_login_service: performing isolated login for %s", settings.test_email)

    auth = AuthService()
    response = auth.login(
        email=settings.test_email,
        password=settings.test_password,
    )

    assert response.status_code == 200, (
        f"fresh_login_service: login failed.\n"
        f"Status: {response.status_code}\n"
        f"Body:   {response.text}"
    )

    token = response.json().get("accessToken", "")
    assert token, "fresh_login_service: login succeeded but 'accessToken' missing."

    auth.set_token(token)
    logger.info("fresh_login_service: isolated token acquired.")
    return auth


# ---------------------------------------------------------------------------
# Resource management fixtures — create & auto-cleanup test data
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def created_book(book_service: BookService) -> str:
    """
    Create a book before a test and delete it in teardown.

    Setup:      POST /api/book with a unique name, then search to retrieve the ID
                (server does not return ID in the create response).
    Yield:      dict with keys: id, name, status, categories, price.
    Teardown:   DELETE /api/book/{id} - ignores 404 if the test already deleted it.

    Used for: TC-BOOK-16, 17, 19-22, 24, 25, 27
    """
    from data.book_data import unique_book_name

    book_name = unique_book_name()
    status = "AVAILABLE"
    categories = ["Technology"]
    price = 150000
    book_id = ""

    with allure.step(f"Fixture setup: create book '{book_name}"):
        create_resp = book_service.create_book(
            name=book_name,
            status=status,
            categories=categories,
            price=price,
        )
        assert create_resp.status_code == 200, (
            f"created_book fixture: failed to create book.\n"
            f"Status: {create_resp.status_code}\n"
            f"Body:   {create_resp.text}"
        )

    with allure.step(f"Fixture setup: resolve ID for '{book_name}'"):
        search_resp = book_service.get_books(search=book_name, limit=5)
        assert search_resp.status_code == 200
        matching = [b for b in search_resp.json().get("list", []) if b["name"] == book_name]
        assert matching, f"create_book fixture: '{book_name}' not found after creation."
        book_id = matching[0]["id"]
        logger.info("create_book fixture: book '%s' created - id=%s", book_name, book_id)

    yield {"id": book_id, "name": book_name, "status": status, "categories": categories, "price": price}

    with allure.step(f"Fixture teardown: delete book id={book_id}"):
        delete_resp = book_service.delete_book(book_id)
        if delete_resp.status_code not in (200, 404):
            logger.warning("created_book teardown: unexpected status %s for id=%s", delete_resp.status_code, book_id)
        else:
            logger.info("Fixture teardown: delete book id=%s > HTTP %s", book_id, delete_resp.status_code)


@pytest.fixture(scope="function")
def create_book_id(book_service: BookService) -> str:
    """
    Create a book before a test and automatically delete it after.
    Returns the book ID.

    Note: server returns only a success message (no ID) - fixture resolves
    the ID via a follow-up search call.
    """
    from data.book_data import unique_book_name

    book_name = unique_book_name("autotest_book_fixture")
    book_id = ""

    with allure.step("Fixture setup: create a book for the test"):
        response = book_service.create_book(
            name=book_name,
            status="AVAILABLE",
            categories=["Technology"],
            price=50000,
        )
        assert response.status_code == 200, (
            f"created_book_id fixture: failed to create book.\n"
            f"Status: {response.status_code}\n"
            f"Body:   {response.text}"
        )
        search_resp = book_service.get_books(search=book_name, limit=5)
        matching = [b for b in search_resp.json().get("list", []) if b["name"] == book_name]
        assert matching, f"create_book_id fixture: '{book_name}' not found after creation."
        book_id = matching[0]["id"]

    yield book_id

    with allure.step(f"Fixture teardown: delete book_id id={book_id}"):
        delete_resp = book_service.delete_book(book_id)
        logger.info("Fixture teardown: delete book_id id=%s > HTTP %s", book_id, delete_resp.status_code)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_id_from_message(message: str) -> str:
    """Legacy helper - kept for backward compatibility. Server no longer returns ID in msg."""
    parts = message.split(": ")
    return parts[-1].strip() if len(parts) >= 2 else ""



@pytest.fixture(scope="function")
def created_category_name(category_service: CategoryService) -> str:
    """
    Create a uniquely named category before a test and delete it after.

    Setup:    POST /api/category-book with a unique name.
    Yield:    The created category name string.
    Teardown: DELETE /api/category-book/{name} regardless of test outcome.

    Args:
        category_service: Authenticated CategoryService from session fixture.

    Returns:
        name (str): The unique name of the newly created category.
    """
    name = unique_category_name("AutoTest_Cat")

    # --- SETUP ---
    with allure.step(f"Fixture setup: create category '{name}'"):
        response = category_service.create_category(name)

        assert response.status_code == 201, (
            f"Fixture failed to create category '{name}'.\n"
            f"Status: {response.status_code}\n"
            f"Body:   {response.text}"
        )
        logger.info("Fixture setup: category '%s' created.", name)

    yield name

    # --- TEARDOWN ---
    with allure.step(f"Fixture teardown: delete category '{name}'"):
        delete_resp = category_service.delete_category(name)
        logger.info(
            "Fixture teardown: delete category '%s' > HTTP %s",
            name,
            delete_resp.status_code,
        )


@pytest.fixture(scope="function")
def created_category_with_book(
        category_service: CategoryService,
        book_service: BookService,
) -> str:
    """
    Create a category and attach a book to it before the test.
    Used for TC-CAT-13: verify delete behavior when bookCount > 0.

    Setup:    Create a unique category, then create a book linked to it.
    Yield:    The created name string.
    Teardown: Attempt to delete the book, then the category.

    Yields:
        name (str): The category name that has at least one book.
    """
    cat_name = unique_category_name("AutoTest_CatWithBook")
    book_id: str = ""

    # -- SETUP: create category ---
    with allure.step(f"Fixture setup: create category '{cat_name}'"):
        cat_resp = category_service.create_category(cat_name)
        assert cat_resp.status_code == 201, (
            f"Fixture failed to create category '{cat_name}'.\n"
            f"Body:   {cat_resp.text}"
        )

    # --- SETUP: create a book linked to this category ---
    with allure.step(f"Fixture setup: create book linked to '{cat_name}'"):
        book_resp = book_service.create_book(
            name=f"AutoTest_Book_for_{cat_name}",
            status="AVAILABLE",
            categories=[cat_name],
            price=50000,
        )

        # BUG-07: Server returns 200 instead of 201 and does not return the book ID.
        # This is marked as xfail as requested. We clean up the category first.
        if book_resp.status_code == 200:
            with allure.step("Fixture teardown (aborted): delete category"):
                category_service.delete_category(cat_name)
            pytest.xfail(
                "BUG-07: Server returns 200 instead of 201 on book creation, "
                "and does not return the created book ID in the message."
            )

        assert book_resp.status_code == 201, (
            f"Fixture failed to create book.\n"
            f"Body:   {book_resp.text}"
        )
        msg: str = book_resp.json().get("msg", "")
        book_id = _extract_id_from_message(msg)
        logger.info(
            "Fixture setup: book '%s' created for category '%s'.",
            book_id,
            cat_name,
        )

    yield cat_name

    # --- TEARDOWN: clean up book first, then category ---
    with allure.step("Fixture teardown: delete book and category"):
        if book_id:
            book_service.delete_book(book_id)
            logger.info("Fixture teardown: book '%s' deleted.", book_id)

        delete_resp = category_service.delete_category(cat_name)
        logger.info(
            "Fixture teardown: delete category '%s' > HTTP %s",
            cat_name,
            delete_resp.status_code,
        )
