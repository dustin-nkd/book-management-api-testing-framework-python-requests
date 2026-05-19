"""
service/category_service.py
---------------------------
Service class for Category Management endpoints.

Endpoints covered:
    GET    /api/category-book        - List all categories.
    POST   /api/category-book        - Create a new category.
    PUT    /api/category-book        - Rename a category.
    DELETE /api/category-book/{name} - Delete a category by name.
"""

import allure
from requests import Response

from clients.base_client import BaseClient


class CategoryService(BaseClient):
    """
    Encapsulates all interactions with the Category Management API.

    Usage:
        cat_svc = CategoryService()
        cat_svc.set_token(access_token)
        response = cat_svc.get_categories()
    """

    _ENDPOINT = "/api/category-book"

    @allure.step("Get all book categories")
    def get_categories(self) -> Response:
        """
        Retrieve the full list of book categories with their book counts.
        This is a public endpoint - no authentication required.

        Returns:
            Response containing 'list' of categories and 'pagination' (HTTP 200).
        """
        return self.get(self._ENDPOINT)

    @allure.step("Create new category: name={name}")
    def create_category(self, name: str) -> Response:
        """
        Create a new book category.
        Requires a valid Bearer token.

        Args:
            name: Display name of the new category. Must be unique.

        Returns:
            Response with a confirmation message on success (HTTP 201).
        """
        payload: dict[str, str] = {"name": name}
        return self.post(self._ENDPOINT, payload=payload)

    @allure.step("Rename category '{name}' > '{new_name}'")
    def update_category(self, name: str, new_name: str) -> Response:
        """
        Rename an existing category using full PUT replacement.

        Args:
            name:     Current category name to look up.
            new_name: Replacement name for the category.

        Returns:
            Response with confirmation message on success (HTTP 200).
        """
        payload: dict[str, str] = {"name": name, "newName": new_name}
        return self.put(self._ENDPOINT, payload=payload)

    @allure.step("Delete category name='{name}'")
    def delete_category(self, name: str) -> Response:
        """
        Delete a category by its name.
        Requires a valid Bearer token.

        Args:
            name: The exact name of the category to delete.

        Returns:
            Response with confirmation message on success (HTTP 200).
        """
        return self.delete(f"{self._ENDPOINT}/{name}")
