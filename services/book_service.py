"""
services/book_service.py
-----------------------
Service class for Book Management endpoints.

Endpoints covered:
    GET    /api/book      - List books (pagination, filter, sort)
    POST   /api/book      - Create a book
    GET    /api/book/{id} - Get a single book by ID
    PATCH  /api/book/{id} - Update a book
    DELETE /api/book/{id} - Delete a book
"""

from typing import Any

import allure
from requests import Response

from clients.base_client import BaseClient


class BookService(BaseClient):
    """
    Encapsulates all interactions with the Book Management API.

    Usage:
        book_svc = BookService()
        book_svc.set_token(access_token)
        response = book_svc.get_books(limit=5, page=1)
    """
    _ENDPOINT = "/api/book"

    @allure.step("Get list of books (limit={limit}, page={page}, search={search})")
    def get_books(
            self,
            limit: int = 10,
            page: int = 1,
            search: str = "",
            sort: str = "updatedAt",
            sort_by: str = "desc",
    ) -> Response:
        """
        Retrieve a paginated list of books with optional filtering and sorting.

        Args:
            limit:   Number of records per page (1-10000). Defaults: 10.
            page:    Page number starting from 1. Defaults: 1.
            search:  Keyword to filter books by name or description.
            sort:    Field to sort by. Options: name, description, status,
                     createdAt, updatedAt, slug, price, currentPrice, viewCount.
            sort_by: Sort direction - 'asc' or 'desc'. Defaults: 'desc'.

        Returns:
            Response containing 'list' array and 'pagination' metadata (HTTP 200).
        """
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "search": search,
            "sort": sort,
            "sortBy": sort_by,
        }
        return self.get(self._ENDPOINT, params=params)

    @allure.step("Get book by ID='{book_id}'")
    def get_book_by_id(self, book_id: str, increment_view: bool = False) -> Response:
        """
        Retrieve detailed information for a single book.

        Args:
            book_id:        Unique identifier for the book (UUID string).
            increment_view: If True, the server increments the book's viewCount.

        Returns:
            Response with full book details including pictures, promotions (HTTP 200).
        """
        params: dict[str, Any] = {"view": str(increment_view).lower()}
        return self.get(f"{self._ENDPOINT}/{book_id}", params=params)

    @allure.step("Create new book: name='{name}'")
    def create_book(
            self,
            name: str,
            status: str,
            categories: list[str],
            price: float,
            slug: str = "",
            description: str = "",
            pictures: list[str] | None = None,
            promotion: list[str] | None = None
    ) -> Response:
        """
        Create a new book entry in the system.
        Requires a valid Bearer token (authenticated user only).

        Args:
            name:        Book title (required).
            status:      Availability status - 'AVAILABLE' or 'UNAVAILABLE' (required).
            categories:  List of category name strings, at least 1 required.
            price:       Base price of the book, max 9,000,000,000,000 (required).
            slug:        URL-friendly identifier. Auto-generated if omitted.
            description: Optional detailed description of the book.
            pictures:    Optional list of file path strings for book cover images.
            promotion:   Optional list of promotion ID strings to attach.

        Returns:
            Response with a confirmation message on success (HTTP 200).
        """
        payload: dict[str, Any] = {
            "name": name,
            "status": status,
            "categories": categories,
            "price": price,
        }

        # Only include optional fields when explicitly provided
        if slug:
            payload["slug"] = slug
        if description:
            payload["description"] = description
        if pictures:
            payload["pictures"] = pictures
        if promotion:
            payload["promotion"] = promotion

        return self.post(self._ENDPOINT, payload=payload)

    @allure.step("Update book ID='{book_id}'")
    def update_book(self, book_id: str, payload: dict[str, Any]) -> Response:
        """
        Partially update a book's fields using PATCH semantics.
        Only the fields included in payload will be modified.
        Requires a valid Bearer token.

        Args:
            book_id:        Unique identifier for the book to update.
            payload:        Dictionary of fields to update. Supported keys:
                            name, slug, description, status, pictures,
                            categories, price, promotion.

        Returns:
            Response with a confirmation message on success (HTTP 200).
        """
        return self.patch(f"{self._ENDPOINT}/{book_id}", payload=payload)

    @allure.step("Delete book ID='{book_id}'")
    def delete_book(self, book_id: str) -> Response:
        """
        Permanently delete a book record by its ID.
        Requires a valid Bearer token.

        Args:
            book_id:        Unique identifier for the book to delete.

        Returns:
            Response with a confirmation message on success (HTTP 200).
        """
        return self.delete(f"{self._ENDPOINT}/{book_id}")
