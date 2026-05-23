"""
data/category_data.py
---------------------
Centralized test data for Category Management tests.
"""

import time


# ---------------------------------------------------------------------------
# Unique name generator
# Using timestamp suffix to avoid conflicts in the shared test environment.
# ---------------------------------------------------------------------------

def unique_category_name(prefix: str = "AutoTest") -> str:
    """
    Generate a unique category name using a timestamp suffix.
    Prevents naming conflicts when running tests against a shared environment.
    
    Args:
        prefix: Human-readable prefix to identitfy the category in the DB.
    
    Returns:
        A unique string in the formot: "{prefix}_{timestamp}"
    """
    return f"{prefix}_{int(time.time())}"


# ---------------------------------------------------------------------------
# Parametrize data: POST /api/category-book — invalid inputs
# Used in: test_category.py::TestCreateCategory::test_create_category_missing_name
# ---------------------------------------------------------------------------

CREATE_CATEGORY_MISSING_FIELD_CASES = [
    (
        "missing_name_field",  # Test case ID shown in Allure/terminal
        {},  # Empty payload - name field omitted entirely
        422,  # Expected status code
        "name",  # Expected field key in 'fields' object
    ),
]

# ---------------------------------------------------------------------------
# Parametrize data: POST /api/category-book — known bugs (blank name inputs)
# These cases expose BUG-01 and BUG-03: server does not validate blank names.
# Marked as xfail in tests — expected to fail until server fixes validation.
# ---------------------------------------------------------------------------

CREATE_CATEGORY_BLANK_NAME_CASES = [
    (
        "empty_string_name",  # TC-CAT-06
        {"name": ""},
    ),
    (
        "whitespace_only_name",  # TC-CAT-11
        {"name": "   "},
    ),
]
