"""
data/book_data.py
-----------------
Centralized test data for Book Management tests.
Keeping test data separate from test logic improves maintainability
and makes it easy to update payloads without touching test files.
"""

# ---------------------------------------------------------------------------
# Valid payloads — expected to succeed (HTTP 201)
# ---------------------------------------------------------------------------

VALID_BOOK_PAYLOAD = {
    "name": "Python Testing with Pytest",
    "status": "AVAILABLE",
    "categories": ["Technology"],
    "price": 150000,
    "description": "A comprehensive guide to testing Python applications.",
    "slug": "python-testing-with-pytest",
}

VALID_BOOK_MINIMAL_PAYLOAD = {
    # Only required fields - no optional fields included
    "name": "Minimal Book",
    "status": "AVAILABLE",
    "categories": ["Technology"],
    "price": 50000,
}

# ---------------------------------------------------------------------------
# Parametrize data for create book tests
# Used in: tests/test_book.py::test_create_book_success
# ---------------------------------------------------------------------------

CREATE_BOOK_VALID_CASES = [
    (
        "full_payload",  # Test case ID shown in Allure/terminal
        {
            "name": "Clean Code",
            "status": "AVAILABLE",
            "categories": ["Technology"],
            "price": 200000,
            "description": "A handbook of agile software craftsmanship.",
        },
        201  # Expected HTTP status code
    ),
    (
        "minimal_required_fields_only",
        {
            "name": "Minimal Required Book",
            "status": "AVAILABLE",
            "categories": ["Technology"],
            "price": 50000,
        },
        201,
    ),
    (
        "unavailable_status",
        {
            "name": "Out of Stock Book",
            "status": "UNAVAILABLE",
            "categories": ["Technology"],
            "price": 75000,
        },
        201,
    ),
]

# ---------------------------------------------------------------------------
# Parametrize data for validation error tests
# Used in: tests/test_book.py::test_create_book_validation_error
# ---------------------------------------------------------------------------

CREATE_BOOK_INVALID_CASES = [
    (
        "missing_name",
        {
            # 'name' field intentionally omitted
            "status": "AVAILABLE",
            "categories": ["Technology"],
            "price": 50000,
        },
        422,  # Expect Unprocessable Entity
    ),
    (
        "missing_categories",
        {
            "name": "Book Without Category",
            "status": "AVAILABLE",
            # 'categories' field intentionally omitted
            "price": 50000,
        },
        422,
    ),
    (
        "missing_price",
        {
            "name": "Book Without Price",
            "status": "AVAILABLE",
            "categories": ["Technology"],
            # 'price' field intentionally omitted
        },
        422,
    ),
    (
        "missing_status_value",
        {
            "name": "Book With Bad Status",
            "status": "INVALID_STATUS",  # Not in enum: AVAILABLE | UNAVAILABLE
            "categories": ["Technology"],
            "price": 50000,
        },
        422,
    ),
    (
        "missing_categories_array",
        {
            "name": "Book With Empty Categories",
            "status": "AVAILABLE",
            "categories": [],  # minItems: 1 per OpenAPI spec
            "price": 50000,
        },
        422,
    ),
]
