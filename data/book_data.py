"""
data/book_data.py
-----------------
Centralized test data for Book Management tests.
"""

import time


# ---------------------------------------------------------------------------
# Unique name generator
# ---------------------------------------------------------------------------

def unique_book_name(prefix: str = "autotest_book") -> str:
    """
    Generate a unique book name using a timestamp suffix.
    Prevents conflicts when running tests against a shared environment.
    """
    return f"{prefix}_{int(time.time())}"


# ---------------------------------------------------------------------------
# Parametrize data: POST /api/book — missing required fields
# Used in: test_book.py::TestCreateBook::test_create_book_missing_required_field
# TC-BOOK-09: missing name | TC-BOOK-10: missing categories
# ---------------------------------------------------------------------------

CREATE_BOOK_MISSING_FIELD_CASES = [
    (
        "missing_name",                         # TC-BOOK-09
        {                                       # Payload with 'name' omitted
            "status": "AVAILABLE",
            "categories": ["Technology"],
            "price": 50000,
        },
        422,
        "name",                                 # Expected key in 'fields' error object
    ),
    (
        "missing_categories",                   # TC-BOOK-10
        {                                       # Payload with 'categories' omitted
            "name": "Book Without Category",
            "status": "AVAILABLE",
            "price": 50000,
        },
        422,
        "categories",
    ),
]

# ---------------------------------------------------------------------------
# Parametrize data: PATCH /api/book/{id} — update individual fields
# Used in: test_book.py::TestUpdateBook::test_update_book_field
# TC-BOOK-19: name | TC-BOOK-20: status | TC-BOOK-21: price | TC-BOOK-22: categories
# ---------------------------------------------------------------------------

UPDATE_BOOK_FIELD_CASES = [
    ("update_name",       {"name": "AutoTest Updated Book Name"}),          # TC-BOOK-19
    ("update_status",     {"status": "UNAVAILABLE"}),                       # TC-BOOK-20
    ("update_price",      {"price": 250000}),                               # TC-BOOK-21
    ("update_categories", {"categories": ["Technology", "Programming"]}),   # TC-BOOK-22
]
