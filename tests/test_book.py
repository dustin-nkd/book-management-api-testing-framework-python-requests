"""
tests/test_book.py
------------------
Automation test script for Book Management endpoints.

Covers:
    GET    /api/book        - list with pagination, search, sort
    POST   /api/book        - create book
    GET    /api/book/{id}   - get single book
    PATCH  /api/book/{id}   - update book
    DELETE /api/book/{id}   - delete book

Manual testing reference: TC-BOOK-01 through TC-BOOK-27
"""

import allure
import pytest

from data.book_data import (
    CREATE_BOOK_MISSING_FIELD_CASES,
    UPDATE_BOOK_FIELD_CASES,
    unique_book_name,
)
from services.book_service import BookService


@allure.epic("Book Management")
class TestGetBooks:
    """TC-BOOK-01 to TC-BOOK-05: GET /api/book"""

    @allure.feature("Get Books")
    @allure.story("Default pagination")
    @allure.title("TC-BOOK-01: GET /api/book with no params returns paginated list")
    @pytest.mark.book
    @pytest.mark.smoke
    def test_get_books_default_pagination(self, book_service: BookService) -> None:
        """
        Verify the default list response contains books and correct pagination metadata.
        Default params: limit=10, page=1.
        """
        response = book_service.get_books()

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert "list" in body
        assert "pagination" in body

        pagination = body["pagination"]
        assert isinstance(pagination["total"], int) and pagination["total"] >= 0
        assert pagination["currentPage"] == 1
        assert isinstance(pagination["totalPage"], int)
        assert pagination["lengthData"] == len(body["list"])

        # Verify each book item has expected fields
        for book in body["list"]:
            for field in ["id", "name", "price", "currentPrice", "viewCount", "categories"]:
                assert field in book, f"Field '{field}' missing from book item."

    @allure.feature("Get Books")
    @allure.story("Custom pagination")
    @allure.title("TC-BOOK-02: GET /api/book with limit=5 and page=2 returns correct slice")
    @pytest.mark.book
    def test_get_books_custom_pagination(self, book_service: BookService) -> None:
        """
        Verify custom limit and page parameters are respected.
        totalPage should recalculate dynamically based on limit.
        """
        response = book_service.get_books(limit=5, page=2)

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        pagination = body["pagination"]

        assert len(body["list"]) <= 5, "More items returned than requested limit."
        assert pagination["totalPage"] >= 1
        assert pagination["lengthData"] == len(body["list"])

    @allure.feature("Get Books")
    @allure.story("Search")
    @allure.title("TC-BOOK-03: GET /api/book?search= filters to matching books only")
    @pytest.mark.book
    def test_get_books_search(self, book_service: BookService, created_book: dict) -> None:
        """
        Verify that search parameter filters books by name.
        Uses a fresh book with a unique name to guarantee a deterministic result.
        """
        book_name = created_book["name"]
        response = book_service.get_books(search=book_name)

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body["pagination"]["totalPage"] >= 1, (
            f"Search for '{book_name}' returned 0 results."
        )
        names_in_list = [b["name"] for b in body["list"]]
        assert book_name in names_in_list, (
            f"Expected '{book_name}' in search results but got: {names_in_list}"
        )

    @allure.feature("Get Books")
    @allure.story("Sort")
    @allure.title("TC-BOOK-04: GET /api/book?sort=name&sortBy=asc returns alphabetical order")
    @pytest.mark.book
    def test_get_books_sort_name_asc(self, book_service: BookService) -> None:
        """
        Verify sort by name ascending - first items should be in alphabetical order.
        To avoid DB collation issues with dirty data (symbols), we verify alphanumeric names.
        """
        response = book_service.get_books(sort="name", sort_by="asc", limit=50)

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )

        names = [b["name"] for b in response.json()["list"]]
        
        # Filter out dirty names starting with special characters to avoid Collation mismatch
        clean_names = [n.lower() for n in names if n and n[0].isalnum()]
        assert clean_names == sorted(clean_names), (
            f"Books are not sorted by name ascending.\nActual order: {clean_names}"
        )

    @allure.feature("Get Books")
    @allure.story("Sort")
    @allure.title("TC-BOOK-05: GET /api/book?sort=price&sortBy=desc returns highest price first")
    @pytest.mark.book
    def test_get_books_sort_price_desc(self, book_service: BookService) -> None:
        """
        Verify sort by price descending - each item's price should be > the next.
        """
        response = book_service.get_books(sort="price", sort_by="desc", limit=10)

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )

        prices = [b["price"] for b in response.json()["list"]]
        for i in range(len(prices) - 1):
            assert prices[i] >= prices[i + 1], (
                f"Price sort broken at index {i}: {prices[i]} < {prices[i + 1]}"
            )


@allure.epic("Book Management")
class TestCreateBook:
    """TC-BOOK-06 to TC-BOOK-15: POST /api/book"""

    @allure.feature("Create Book")
    @allure.story("Valid full payload")
    @allure.title("TC-BOOK-06: Create book with all fields should return 200")
    @pytest.mark.book
    def test_create_book_with_full_payload(self, book_service: BookService) -> None:
        """
        Verify a new book is created with all available fields.
        Note: server returns 200 (not 201) and does not include boook ID in response.
        """
        book_name = unique_book_name("autotest_full")
        book_id = None

        try:
            response = book_service.create_book(
                name=book_name,
                status="AVAILABLE",
                categories=["Technology"],
                price=150000,
                slug=f"autotest-full-{int(__import__('time').time())}",
                description="AutoTest book with all optional fields.",
            )

            assert response.status_code == 200, (
                f"Expected 200 but got {response.status_code}: {response.text}"
            )
            assert response.json().get("msg") == "Book created successfully."

            # Resolve ID for teardown
            search = book_service.get_books(search=book_name, limit=5)
            matching = [b for b in search.json().get("list", []) if b["name"] == book_name]
            if matching:
                book_id = matching[0]["id"]
        finally:
            if book_id:
                book_service.delete_book(book_id)

    @allure.feature("Create Book")
    @allure.story("Require fields only")
    @allure.title("TC-BOOK-07: Create book with required fields only should return 200")
    @pytest.mark.book
    def test_create_book_with_required_fields_only(self, book_service: BookService) -> None:
        """
        Verify slug, description, pictures, promotions are truly optional.
        """
        book_name = unique_book_name("autotest_min")
        book_id = None

        try:
            response = book_service.create_book(
                name=book_name,
                status="AVAILABLE",
                categories=["Technology"],
                price=150000,
            )

            assert response.status_code == 200, (
                f"Expected 200 but got {response.status_code}: {response.text}"
            )
            assert response.json().get("msg") == "Book created successfully."

            search = book_service.get_books(search=book_name, limit=5)
            matching = [b for b in search.json().get("list", []) if b["name"] == book_name]
            if matching:
                book_id = matching[0]["id"]
        finally:
            if book_id:
                book_service.delete_book(book_id)

    @allure.feature("Create Book")
    @allure.story("Unavailable status")
    @allure.title("TC-BOOK-08: Create book with status=UNAVAILABLE should return 200")
    @pytest.mark.book
    def test_create_book_unavailable_status(self, book_service: BookService) -> None:
        """
        Verify both enum values for status are accepted: AVAILABLE and UNAVAILABLE.
        """
        book_name = unique_book_name("autotest_unavail")
        book_id = None

        try:
            response = book_service.create_book(
                name=book_name,
                status="UNAVAILABLE",
                categories=["Technology"],
                price=75000,
            )

            assert response.status_code == 200, (
                f"Expected 200 but got {response.status_code}: {response.text}"
            )
            assert response.json().get("msg") == "Book created successfully."

            search = book_service.get_books(search=book_name, limit=5)
            matching = [b for b in search.json().get("list", []) if b["name"] == book_name]
            if matching:
                book_id = matching[0]["id"]
        finally:
            if book_id:
                book_service.delete_book(book_id)

    @allure.feature("Create Book")
    @allure.story("Validation error - missing required field")
    @allure.title("TC-BOOK-09/10: Create book with missing required field should return 422")
    @pytest.mark.book
    @pytest.mark.parametrize(
        "case_id, payload, expected_status, expected_field",
        CREATE_BOOK_MISSING_FIELD_CASES,
        ids=[c[0] for c in CREATE_BOOK_MISSING_FIELD_CASES],
    )
    def test_create_book_missing_required_field(
            self,
            book_service: BookService,
            case_id: str,
            payload: dict,
            expected_status: int,
            expected_field: str,
    ) -> None:
        """
        Verify that omitting a required field (name or categories) returns 422.
        Error messages follow the pattern from auth and vary by field type:
        - string: "Expected property '{field}' to be string but found: undefined"
        - array: "Expected array"
        """
        response = book_service.post("/api/book", payload=payload)

        assert response.status_code == expected_status, (
            f"[{case_id}] Expected {expected_status}"
            f"but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Invalid data."
        assert "fields" in body
        assert expected_field in body["fields"], (
            f"[{case_id}] Expected {expected_field} in fields but got: {body['fields']}"
        )

    @allure.feature("Create Book")
    @allure.story("Required field not validated - missing price")
    @allure.title("TC-BOOK-11: Missing price field should return 422 - BUG")
    @pytest.mark.book
    @pytest.mark.xfail(
        reason=(
            "BUG: POST /api/book does not validate 'price' as required. "
            "Server returns 200 and creates the book without a price, "
            "resulting in an unexpected default value and negative currentPrice."
        ),
        strict=False,
    )
    def test_create_book_missing_price_not_validated(
            self, book_service: BookService
    ) -> None:
        """
        Verify that missing 'price' is rejected with 422.
        Currently xfail: server accepts the request and creates the book anyway.
        """
        book_name = unique_book_name("autotest_no_price")
        book_id = None

        try:
            response = book_service.post("/api/book", payload={
                "name": book_name,
                "status": "AVAILABLE",
                "categories": ["Technology"],
            })

            if response.status_code == 200:
                allure.attach(
                    body=(
                        "BUG: POST /api/book createad a book without 'price'.\n"
                        "Server returned 200 instead of 422.\n"
                        "This results in an unexpected default price and potentiallly "
                        "negative currentPrice values."
                    ),
                    name="⚠️ Bug — price not validated as required",
                    attachment_type=allure.attachment_type.TEXT,
                )
                search = book_service.get_books(search=book_name, limit=5)
                matching = [b for b in search.json().get("list", []) if b["name"] == book_name]
                if matching:
                    book_id = matching[0]["id"]

            assert response.status_code == 422, (
                f"Expected 422 but got {response.status_code}: {response.text}"
            )
        finally:
            if book_id:
                book_service.delete_book(book_id)

    @allure.feature("Create Book")
    @allure.story("Required field not validated - missing status")
    @allure.title("TC-BOOK-12: Missing status field should return 422 - BUG")
    @pytest.mark.book
    @pytest.mark.xfail(
        reason=(
            "BUG: POST /api/book does not validate 'status' as required. "
            "Server returns 200 and creates the book without a status value."
        ),
        strict=False,
    )
    def test_create_book_missing_status_not_validated(
            self, book_service: BookService
    ) -> None:
        """
        Verify that missing 'status' is rejected with 422.
        Currently xfail: server accepts the request and creates the book anyway.
        Note: an invalid status IS rejected (TC-BOOK-13) - only missing is bypassed.
        """
        book_name = unique_book_name("autotest_no_status")
        book_id = None

        try:
            response = book_service.post("/api/book", payload={
                "name": book_name,
                "categories": ["Technology"],
                "price": 50000,
            })

            if response.status_code == 200:
                allure.attach(
                    body=(
                        "BUG: POST /api/book createad a book without 'status'.\n"
                        "Server returned 200 instead of 422.\n"
                    ),
                    name="⚠️ Bug — status not validated as required",
                    attachment_type=allure.attachment_type.TEXT,
                )
                search = book_service.get_books(search=book_name, limit=5)
                matching = [b for b in search.json().get("list", []) if b["name"] == book_name]
                if matching:
                    book_id = matching[0]["id"]

            assert response.status_code == 422, (
                f"Expected 422 but got {response.status_code}: {response.text}"
            )
        finally:
            if book_id:
                book_service.delete_book(book_id)

    @allure.feature("Create Book")
    @allure.story("Validation error - invalid status enum")
    @allure.title("TC-BOOK-13: Create book with invalid status value should return 422")
    @pytest.mark.book
    def test_create_book_invalid_status_enum(self, book_service: BookService) -> None:
        """
        Verify that an invalid status string is rejected with 422.
        Note: missing status is NOT validated (TC-BOOK-12 bug), but invalid valus IS.
        Error message for enum: "Expected kind 'UnionEnum'"
        """
        response = book_service.create_book(
            name="Book With Invalid Status",
            status="PENDING_APPROVAL",
            categories=["Technology"],
            price=50000,
        )

        assert response.status_code == 422, (
            f"Expected 422 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Invalid data."
        assert "fields" in body
        assert "status" in body["fields"]
        assert body["fields"]["status"] == ["Expected kind 'UnionEnum'"]

    @allure.feature("Create Book")
    @allure.story("Validation error - empty categories array")
    @allure.title("TC-BOOK-14: Create book with empty categories array should return 422")
    @pytest.mark.book
    def test_create_book_empty_categories(self, book_service: BookService) -> None:
        """
        Verify that categories: [] (empty array) is rejected.
        minItems: 1 constraint must be enforced.
        Error message: "Expected array length to be greater or equal to 1"
        """
        response = book_service.create_book(
            name="Book With Empty Categories",
            status="AVAILABLE",
            categories=[],
            price=50000,
        )

        assert response.status_code == 422, (
            f"Expected 422 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("msg") == "Invalid data."
        assert "fields" in body
        assert "categories" in body["fields"]
        assert body["fields"]["categories"] == [
            "Expected array length to be greater or equal to 1",
        ]

    @allure.feature("Create Book")
    @allure.story("Unauthenticated")
    @allure.title("TC-BOOK-15: POST /api/book without token should return 401")
    @pytest.mark.book
    def test_create_book_no_token(self) -> None:
        """
        Verify that POST /api/book returns 401 when no Authorization header is provided.
        """
        auth = BookService()
        response = auth.create_book(
            name="Unauthorized Book",
            status="AVAILABLE",
            categories=["Technology"],
            price=50000,
        )

        assert response.status_code == 401, (
            f"Expected 401 but got {response.status_code}: {response.text}"
        )
        assert  response.json().get("msg") == "Missing or invalid Authorization header"


@allure.epic("Book Management")
class TestGetBookById:
    """TC-BOOK-16 to TC-BOOK-18: GET /api/book/{id}"""

    @allure.feature("Get Book by ID")
    @allure.story("Valid ID")
    @allure.title("TC-BOOK-16: GET /api/book/{id} returns full book detail object")
    @pytest.mark.book
    @pytest.mark.smoke
    def test_get_book_by_id(self, book_service: BookService, created_book: dict) -> None:
        """
        Verify GET /api/book/{id} returns all expected fields for a valid book.
        Note: detail response includes 'auth' and 'picture' (as file metadata objects)
        but does NOT include 'slug' (present in list response only).
        """
        book_id = created_book["id"]
        response = book_service.get_book_by_id(book_id)

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )

        body = response.json()
        for field in ["id", "name", "description", "status", "price",
                      "currentPrice", "viewCount", "categories", "picture",
                      "auth", "promotions", "createdAt", "updatedAt"]:
            assert field in body, f"Field '{field}' missing from detail response."

        assert body["id"] == book_id
        assert body["name"] == created_book["name"]
        assert body["status"] == created_book["status"]
        assert body["price"] == created_book["price"]
        assert isinstance(body["viewCount"], int)
        assert isinstance(body["auth"], dict)
        assert isinstance(body["picture"], list)

    @allure.feature("Get Book by ID")
    @allure.story("View count increment")
    @allure.title("TC-BOOK-17: GET /api/book/{id}?view=true increments viewCount by 1")
    @pytest.mark.book
    def test_get_book_view_count_increment(
            self, book_service: BookService, created_book: dict) -> None:
        """
        Verify that ?view=true increments the book's viewCount.
        Freshly  created books start at viewCount=0
        """
        book_id = created_book["id"]

        # Get current viewCount (should be 0 for fresh book)
        before = book_service.get_book_by_id(book_id).json()["viewCount"]

        # Call with view=true
        response = book_service.get_book_by_id(book_id, increment_view=True)

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )
        after = response.json()["viewCount"]
        assert after == before + 1, (
            f"viewCount did not increment. before={before}, after={after}"
        )

    @allure.feature("Get Book by ID")
    @allure.story("Non-existent ID")
    @allure.title("TC-BOOK-18: GET /api/book/{id} with non-existent ID should return 404")
    @pytest.mark.book
    def test_get_book_not_existent_id(self, book_service: BookService) -> None:
        """
        Verify that requesting a non-existent book ID returns 404.
        """
        response = book_service.get_book_by_id("nonexistent-uuid-xyz")

        assert response.status_code == 404, (
            f"Expected 404 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Book not found."


@allure.epic("Book Management")
class TestUpdateBook:
    """TC-BOOK-19 to TC-BOOK-24: PATCH /api/book/{id}"""

    @allure.feature("Update Book")
    @allure.story("Update individual fields")
    @allure.title("TC-BOOK-19/20/21/22: Update book field should return 200")
    @pytest.mark.book
    @pytest.mark.parametrize(
        "case_id, payload",
        UPDATE_BOOK_FIELD_CASES,
        ids=[c[0] for c in UPDATE_BOOK_FIELD_CASES]
    )
    def test_update_book_field(
            self,
            book_service: BookService,
            created_book: dict,
            case_id: str,
            payload: dict
    ) -> None:
        """
        Verify that each field (name, status, price, categories) can be updated individually.
        Each parameter case gets its own fresh book via the created_book fixture.
        """
        book_id = created_book["id"]
        response = book_service.update_book(book_id, payload)

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Book updated successfully."

    @allure.feature("Update Book")
    @allure.story("Non-existent ID")
    @allure.title("TC-Book-23: PATCH /api/book/{id} with non-existent ID should return 404")
    @pytest.mark.book
    def test_get_book_nonexistent_id(self, book_service: BookService) -> None:
        """
        Verify that attempting to update a non-existent book returns 404.
        """
        response = book_service.update_book(
            "nonexistent-uuid-xyz",
            {"name": "Nonexistent Book"},
        )

        assert response.status_code == 404, (
            f"Expected 404 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Book not found."

    @allure.feature("Update Book")
    @allure.story("Unauthenticated")
    @allure.title("TC-BOOK-24: PATCH /api/book/{id} without token should return 401")
    @pytest.mark.book
    def test_update_book_no_token(self, created_book: dict) -> None:
        """
        Verify that PATCH /api/book/{id} returns 401 when no token is provided.
        """
        book_id = created_book["id"]
        auth = BookService()
        response = auth.update_book(book_id, {"name": "Unauthorized Update"})

        assert response.status_code == 401, (
            f"Expected 401 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Missing or invalid Authorization header"


@allure.epic("Book Management")
class TestDeleteBook:
    """TC-BOOK-25 to TC-BOOK-27: DELETE /api/book/{id}"""

    @allure.feature("Delete Book")
    @allure.story("Existing Book")
    @allure.title("TC-BOOK-25: DELETE /api/book/{id} with valid ID should return 200")
    @pytest.mark.book
    def test_delete_book(
            self, book_service: BookService, created_book: dict
    ) -> None:
        """
        Verify that an existing book can be deleted.
        The created_book fixture teardown will receive a 404 (already deleted) - this is expected.
        """
        book_id = created_book["id"]
        response = book_service.delete_book(book_id)

        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Deleted successfully."

        # Verify deletion - GET should return 404
        verify = book_service.get_book_by_id(book_id)
        assert verify.status_code == 404, (
            f"Expected 404 after deletion but got {verify.status_code}."
        )

    @allure.feature("Delete Book")
    @allure.story("Non-existing ID")
    @allure.title("TC-BOOK-26: DELETE /api/book/{id} with non-existent ID should return 404")
    @pytest.mark.book
    def test_delete_book_nonexistent_id(self, book_service: BookService) -> None:
        """Verify that attempting to delete a non-existent book returns 404."""
        response = book_service.delete_book("nonexistent-uuid-xyz")

        assert response.status_code == 404, (
            f"Expected 404 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Book not found."

    @allure.feature("Delete Book")
    @allure.story("Unauthenticated")
    @allure.title("TC-BOOK-26: DELETE /api/book/{id} without token should return 401")
    @pytest.mark.book
    def test_delete_book_no_token(self, created_book: dict) -> None:
        """
        Verify that DELETE /api/book/{id} returns 401 when no token is provided.
        """
        book_id = created_book["id"]
        auth = BookService()
        response = auth.delete_book(book_id)

        assert response.status_code == 401, (
            f"Expected 401 but got {response.status_code}: {response.text}"
        )
        assert response.json().get("msg") == "Missing or invalid Authorization header"