"""
tests/test_category.py
----------------------
Automation test script for Category Management endpoints.

Covers:
    GET    /api/category-book
    POST   /api/category-book
    PUT    /api/category-book
    DELETE /api/category-book/{name}

Manual testing reference: TC-CAT-01 through TC-CAT-13
"""

import allure
import pytest

from data.category_data import (
    CREATE_CATEGORY_BLANK_NAME_CASES,
    CREATE_CATEGORY_MISSING_FIELD_CASES,
    unique_category_name,
)
from services.category_service import CategoryService


@allure.epic("Category Management")
class TestGetCategories:
    """TC-CAT-01: GET /api/category-book"""

    @allure.feature("Get Categories")
    @allure.story("Get all categories")
    @allure.title("TC-CAT-01: GET /api/category-book should return list with bookCount")
    @pytest.mark.smoke
    @pytest.mark.category
    def test_get_all_categories_success(
            self,
    ) -> None:
        """
        Verify public endpoint returns a list of categories.
        No authentication required.
        Each item must have 'name' (str) and 'bookCount' (int).
        Pagination must contain 'total'.
        """
        # Use a standalone unauthenticated service to confirm endpoint is public
        cat_service = CategoryService()
        response = cat_service.get_categories()

        assert response.status_code == 200

        body = response.json()

        # Verify top-level structure
        assert "list" in body, "Response missing 'list' key."
        assert "pagination" in body, "Response missing 'pagination' key."

        # Verify pagination contains 'total' (Category API only returns total,
        # unlike Book API which also returns totalPage, currentPage, lengthData)
        assert "total" in body["pagination"], "Response missing 'total' key."
        assert body["pagination"]["total"] >= 0

        # Verify each category item has required fields with correct types
        for item in body["list"]:
            assert "name" in item, f"Category item missing 'name': {item}"
            assert isinstance(item["name"], str)
            assert isinstance(item["bookCount"], int)


@allure.epic("Category Management")
class TestCreateCategory:
    """TC-CAT-02 to TC-CAT-05, TC-CAT-11: POST /api/category-book"""

    @allure.feature("Create Category")
    @allure.story("Create with valid name")
    @allure.title("TC-CAT-02: Create category with valid unique name should return 201")
    @pytest.mark.category
    def test_create_category_valid_name(
            self,
            category_service: CategoryService,
    ) -> None:
        """
        Verify a new category is created successfully with a unique name.
        Cleanup is handled manually here since we use a direct service call.
        """
        name = unique_category_name("AutoTest_Valid")

        response = category_service.create_category(name)

        assert response.status_code == 201
        assert response.json().get("msg") == "Category created successfully."

        # Teardown: remove the created category to keep the environment clean
        category_service.delete_category(name)

    @allure.feature("Create Category")
    @allure.story("Create with duplicate name")
    @allure.title("TC-CAT-03: Create category with duplicate name should return 400")
    @pytest.mark.category
    def test_create_category_duplicate_name(
            self,
            category_service: CategoryService,
            created_category_name: str,
    ) -> None:
        """
        Verify that creating a category with an already existing name
        is rejected with 400 and a clear error message.
        Uses 'created_category_name' fixture for the pre-existing category.
        """
        # Attempt to create a second category with the exact same name
        response = category_service.create_category(created_category_name)

        assert response.status_code == 400
        assert response.json().get("msg") == "Category already exists."

    @allure.feature("Create Category")
    @allure.story("Validate error - missing required field")
    @allure.title("TC-CAT-04: Create category with missing name field should return 422")
    @pytest.mark.category
    @pytest.mark.parametrize(
        "case_id, payload, expected_status, expected_field",
        CREATE_CATEGORY_MISSING_FIELD_CASES,
        ids=[c[0] for c in CREATE_CATEGORY_MISSING_FIELD_CASES],
    )
    def test_create_category_missing_name(
            self,
            category_service: CategoryService,
            case_id: str,
            payload: dict,
            expected_status: int,
            expected_field: str,
    ) -> None:
        """
        Verify that omitting the required 'name' field triggers a 422
        response with a descriptive 'fields' validation object.
        """
        response = category_service.post("/api/category-book", payload=payload)

        assert response.status_code == expected_status

        body = response.json()
        assert "fields" in body, "Expected 'fields' key in 422 response body."
        assert expected_field in body["fields"], (
            f"Expected '{expected_field}' in fields but got {body['fields']}"
        )

    @allure.feature("Create Category")
    @allure.story("Validate error - blank name input")
    @allure.title("TC-CAT-05 & TC-CAT-11: Blank name inputs should be rejected with 422")
    @pytest.mark.category
    @pytest.mark.xfail(
        reason=(
                "BUG-01 / BUG-03: Server does not validate blank or whitespace-only "
                "category names. Input is accepted as valid if not already in DB. "
                "Expected: 422. Actual: 201 (created) or 400 (duplicate if it exists)."
        ),
        strict=False,
    )
    @pytest.mark.parametrize(
        "case_id, payload",
        CREATE_CATEGORY_BLANK_NAME_CASES,
        ids=[c[0] for c in CREATE_CATEGORY_BLANK_NAME_CASES],
    )
    def test_create_blank_name_should_be_rejected(
            self,
            category_service: CategoryService,
            case_id: str,
            payload: dict,
    ) -> None:
        """
        Verify that blank or white-space names are rejected with 422.

        Currently marked xfail due to BUG-01 / BUG-03:
        Server lacks input sanitization - blank strings pass through
        to DB lookup instead of being rejected at validation layer.
        """
        response = category_service.post("/api/category-book", payload=payload)

        # This assertion documents the EXPECTED behavior post-bug-fix
        assert response.status_code == 422, (
            f"Expected 422 for blank name input '{payload}' "
            f"but got {response.status_code}: {response.text}"
        )


@allure.epic("Category Management")
class TestUpdateCategory:
    """TC-CAT-06 to TC-CAT-08, TC-CAT-12: PUT /api/category-book"""

    @allure.feature("Update Category")
    @allure.story("Valid rename")
    @allure.title("TC-CAT-06: Rename existing category should return 200")
    @pytest.mark.category
    def test_update_category_valid_rename(
            self,
            category_service: CategoryService,
            created_category_name: str,
    ) -> None:
        """
        Verify an existing category can be renamed successfully.
        The fixture creates the original category and cleans up using
        the NEW name, so we update the fixture teardown target via rename.
        """
        new_name = unique_category_name("AutoTest_Renamed")

        response = category_service.update_category(
            name=created_category_name,
            new_name=new_name,
        )

        assert response.status_code == 200
        assert response.json().get("msg") == "Category updated successfully."

        # Cleanup: delete the renamed category since fixture will try old name
        # (old name no longer exists after rename)
        category_service.delete_category(new_name)

    @allure.feature("Update Category")
    @allure.story("Name does not exist")
    @allure.title("TC-CAT-07: Rename non-existent category should return 400")
    @pytest.mark.category
    def test_update_category_name_not_found(
            self,
            category_service: CategoryService,
    ) -> None:
        """
        Verify that attempting to rename a non-existent category
        returns 400 with "Invalid data." message.
        Note: Server returns 400 (not 404) for this case - confirmed in manual testing.
        """
        response = category_service.update_category(
            name="NonExistentCategory_AutoTest_XYZ",
            new_name="Whatever_AutoTest",
        )

        assert response.status_code == 400
        assert response.json().get("msg") == "Invalid data."

    @allure.feature("Update Category")
    @allure.story("Validation error - missing newName field")
    @allure.title("TC-CAT-08: Update category without newName should return 422")
    @pytest.mark.category
    def test_update_category_missing_new_name(
            self,
            category_service: CategoryService,
            created_category_name: str,
    ) -> None:
        """
        Verify that omitting 'newName' from the PUT request body
        returns 422 with a descriptive field-level validation error.
        """
        # Send only 'name', intentionally omitting 'newName'
        response = category_service.put(
            "/api/category-book",
            payload={"name": created_category_name},
        )

        assert response.status_code == 422

        body = response.json()
        assert "fields" in body
        assert "newName" in body["fields"], (
            f"Expected 'newName' in fields but got {body['fields']}"
        )

    @allure.feature("Update Category")
    @allure.story("Duplicate new name")
    @allure.title("TC-CAT-12: Rename category to an existing category name should return 400")
    @pytest.mark.category
    def test_update_category_duplicate_new_name(
            self,
            category_service: CategoryService,
            created_category_name: str,
    ) -> None:
        """
        Verify that renaming a category to a name that already exists is rejected.
        """
        # Create a second category to serve as the duplicate target
        target_name = unique_category_name("AutoTest_DuplicateTarget")
        category_service.create_category(target_name)

        try:
            response = category_service.update_category(
                name=created_category_name,
                new_name=target_name,
            )
            assert response.status_code == 400
            assert response.json().get("msg") == "Category already exists."
        finally:
            # Clean up the target category
            category_service.delete_category(target_name)


@allure.epic("Category Management")
class TestDeleteCategory:
    """TC-CAT-09, TC-CAT-10, TC-CAT-13: DELETE /api/category-book/{name}"""

    @allure.feature("Delete Category")
    @allure.story("Delete existing category")
    @allure.title("TC-CAT-09: Delete existing category should return 200")
    @pytest.mark.category
    def test_delete_category_exists(
            self,
            category_service: CategoryService,
            created_category_name: str,
    ) -> None:
        """
        Verify that an existing category can be deleted successfully.
        The fixture creates the category: this test deletes it directly.
        Fixture teardown will attempt deletion again but 404 is acceptable.
        """
        response = category_service.delete_category(name=created_category_name)

        assert response.status_code == 200
        assert response.json().get("msg") == "Category deleted successfully."

    @allure.feature("Delete Category")
    @allure.story("Delete non-existing category")
    @allure.title("TC-CAT-10: Delete non-existing category should return 404")
    @pytest.mark.category
    def test_delete_category_not_found(
            self,
            category_service: CategoryService,
    ) -> None:
        """
        Verify that attempting to delete a non-existent category
        returns 404 with a clear "Category not found." message.
        """
        response = category_service.delete_category(
            "NonExistentCategory_AutoTest_XYZ"
        )

        assert response.status_code == 404
        assert response.json().get("msg") == "Category not found."

    @allure.feature("Delete category")
    @allure.story("Delete category with associated books")
    @allure.title("TC-CAT-13: Delete category with books - Observe system behavior")
    @pytest.mark.category
    def test_delete_category_with_books(
            self,
            category_service: CategoryService,
            created_category_with_book: str,
    ) -> None:
        """
        Observe and document server behavior when deleting a category
        that has at least one book associated (bookCount > 0).

        BUG-05: Server allows deletion without any warning or protection.
        This test documents the actual behavior rather than asserting
        an ideal behavior - serving as a regression guard.

        If this test starts failing with 400 in the future, it means
        the server has added proper protection (which is the desired fix).
        """
        response = category_service.delete_category(created_category_with_book)

        # Document actual behavior: server returns 200 (force delete, no protection)
        # If server is fixed to return 400, update this assertion accordingly.
        assert response.status_code == 200, (
            f"Observed behavior changed - server now returns "
            f"{response.status_code}: {response.text}. "
            f"Update assertion if protection has been added."
        )

        # Attach a note to the Allure report for visibility
        allure.attach(
            body=(
                "BUG-05: Server allows deletion of category with bookCount > 0.\n "
                "Associated book may become orphaned after this operation.\n"
                "Expected: 400 with message blocking deletion, or cascade warning."
            ),
            name="⚠️ Known Bug — No deletion protection",
            attachment_type=allure.attachment_type.TEXT,
        )
