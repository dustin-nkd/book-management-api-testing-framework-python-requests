"""
services/auth_service.py
------------------------
Service class for Authentication Management endpoints.

Endpoints covered:
    POST   /api/login
    POST   /api/register
    POST   /api/refetch-token
    GET    /api/me
    PATCH  /api/profile
    DELETE /api/logout
"""

from typing import Any

import allure
from requests import Response

from clients.base_client import BaseClient


class AuthService(BaseClient):
    """
    Encapsulates all interactions with the Authentication API.

    Usage:
        auth = AuthService()
        response = auth.login("user@example.com", "secret")
        token = response.json()["accessToken"]
        auth.set_token(token)
    """

    # Base path prefix shared by all auth endpoints
    _BASE = ""

    @allure.step("Login with email='{email}'")
    def login(self, email: str, password: str) -> Response:
        """
        Authenticate a user and retrieve a JWT access token.

        Args:
            email:    User's email address.
            password: User's plain-text password.

        Returns:
            Response with 'accessToken' and 'exp' on success (HTTP 200).
        """
        payload: dict[str, str] = {"email": email, "password": password}
        return self.post("/api/login", payload=payload)

    @allure.step("Register new user: name='{name}', email='{email}'")
    def register(
            self,
            name: str,
            email: str,
            password: str,
            avatar_url: str = "",
            phone: str = "",
            address: str = "",
    ) -> Response:
        """
        Register a new user account.

        Args:
            name: Display name of the new user.
            email: Unique email address.
            password: Plain-text password (min length depends on server policy).
            avatar_url: Optional URL pointing to the user's avatar image.
            phone: Optional phone number.
            address: Optional address string.

        Returns:
            Response with a confirmation message on success (HTTP 200).
        """
        payload: dict[str, Any] = {
            "name": name,
            "email": email,
            "password": password
        }

        # Only include optional fields if they are provided to keep payload clean
        if avatar_url:
            payload["avatarUrl"] = avatar_url
        if phone:
            payload["phone"] = phone
        if address:
            payload["address"] = address

        return self.post("/api/register", payload=payload)

    @allure.step("Get current authenticated user profile (/api/me)")
    def get_me(self) -> Response:
        """
        Retrieve profile information of the currently authenticated user.
        Requires a valid Bearer token to be set on the session.

        Returns:
            Response containing user id, name, email, etc. (HTTP 200).
        """
        return self.get("/api/me")

    @allure.step("Update profile")
    def update_profile(self, payload: dict[str, Any]) -> Response:
        """
        Update the current user's profile fields.
        Requires a valid Bearer token.

        Args:
            payload: Dictionary of fields to update. Supported keys:
                     name, email, password, password_old,
                     avatarUrl, phone, address, config.

        Returns:
            Response with confirmation message on success (HTTP 200).
        """
        return self.patch("/api/profile", payload=payload)

    @allure.step("Logout current session")
    def logout(self) -> Response:
        """
        Invalidate the current session and clear stored tokens.

        Returns:
            Response with confirmation message on success (HTTP 200).
        """
        return self.delete("/api/logout")
