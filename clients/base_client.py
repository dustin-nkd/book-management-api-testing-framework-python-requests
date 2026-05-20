"""
clients/base_client.py
----------------------
Base HTTP client that wraps the 'requests' library.

Responsibilities:
- Provide reusable GET, POST, PUT, PATCH, DELETE methods.
- Automatically attach Authorization headers when a token is provided.
- Integrate with Allure to log request/response details into test reports.
- Apply global timeout and SSL settings from config.
"""

import json
from typing import Any

import allure
import requests
import urllib3
from requests import Response, Session

from config import settings
from utils.logger import get_logger

# Suppress only the InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger(__name__)


class BaseClient:
    """
    A wrapper around the 'requests.Session' providing:
    - Automatic base URL resolution.
    - Allure step logging for every HTTP call.
    - Centralizedd error handling and response loggin.
    - Optional Bearer token injection via 'set_token()'.
    """

    def __init__(self) -> None:
        # Use a Session to persist headers and connection pooling across requests
        self._session: Session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})
        self._base_url: str = settings.base_url
        self._timeout: int = settings.request_timeout
        self._verify_ssl: bool = settings.verify_ssl

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def set_token(self, token: str) -> None:
        """
        Inject Bearer token into the session's default headers.
        Once set, every subsequent request will carry this token.

        Args:
            token: JWT access token returned from the login endpoint.
        """
        self._session.headers.update({"Authorization": f"Bearer {token}"})
        logger.debug("Bearer token has been set on the session.")

    def clear_token(self) -> None:
        """Remove the Authorization header from the session."""
        self._session.headers.pop("Authorization", None)
        logger.debug("Bearer token cleared from session.")

    # ------------------------------------------------------------------
    # HTTP methods
    # ------------------------------------------------------------------

    def get(
            self,
            endpoint: str,
            params: dict[str, Any] | None = None,
            **kwargs: Any,
    ) -> Response:
        """
        Send an HTTP GET request.

        Args:
            endpoint: API path relative to base URL (e.g. '/api/book').
            params:   Query string parameters as a dictionary.
            **kwargs: Extra arguments forwarded to requests.Session.request().

        Returns:
            requests.Response object.
        """
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(
            self,
            endpoint: str,
            payload: dict[str, Any] | None = None,
            **kwargs: Any,
    ) -> Response:
        """
        Send an HTTP POST request with a JSON body.

        Args:
            endpoint: API path relative to base URL.
            payload:  Request body serialized as JSON.
            **kwargs: Extra arguments forwarded to requests.Session.request().

        Returns:
            requests.Response object.
        """
        return self._request("POST", endpoint, json=payload, **kwargs)

    def put(
            self,
            endpoint: str,
            payload: dict[str, Any] | None = None,
            **kwargs: Any,
    ) -> Response:
        """
        Send an HTTP PUT request with a JSON body.

        Args:
            endpoint: API path relative to base URL.
            payload:  Request body serialized as JSON.
            **kwargs: Extra arguments forwarded to requests.Session.request().

        Returns:
            requests.Response object.
        """
        return self._request("PUT", endpoint, json=payload, **kwargs)

    def patch(
            self,
            endpoint: str,
            payload: dict[str, Any] | None = None,
            **kwargs: Any,
    ) -> Response:
        """
        Send an HTTP PATCH request with a JSON body.

        Args:
            endpoint: API path relative to base URL.
            payload:  Request body serialized as JSON.
            **kwargs: Extra arguments forwarded to requests.Session.request().

        Returns:
            requests.Response object.
        """
        return self._request("PATCH", endpoint, json=payload, **kwargs)

    def delete(
            self,
            endpoint: str,
            params: dict[str, Any] | None = None,
            **kwargs: Any,
    ) -> Response:
        """
        Send an HTTP PATCH request with a JSON body.

        Args:
            endpoint: API path relative to base URL.
            params:   Query string parameters as a dictionary.
            **kwargs: Extra arguments forwarded to requests.Session.request().

        Returns:
            requests.Response object.
        """
        return self._request("DELETE", endpoint, params=params, **kwargs)

    # ------------------------------------------------------------------
    # Core private method
    # ------------------------------------------------------------------

    def _request(
            self,
            method: str,
            endpoint: str,
            **kwargs: Any,
    ) -> Response:
        """
        Core dispatcher: builds the full URL, executes the request,
        logs details to both the terminal and Allure repport.

        This method is intentionally private - all public HTTP methods
        route through here to guarantee consistent logging behavior.

        Args:
            method:   HTTP verb: (GET, POST, PUT, PATCH, DELETE.)
            endpoint: API path relative to base URL.
            **kwargs: Forwarded directly to requests.Session.request().

        Returns:
            requests.Response object.


        Raises:
            requests.exceptions.Timeout:          If the request exceeds self._timeout.
            requests.exceptions.ConnectionError:  If the request is unreachable.
            requests.exceptions.RequestException: For any other transport-level error.
        """
        url = f"{self._base_url}{endpoint}"

        # Attach global defaults unless the caller explicitly overrides them
        kwargs.setdefault("timeout", self._timeout)
        kwargs.setdefault("verify", self._verify_ssl)

        # Allure step wraps the entire request/response cycle
        with allure.step(f"[{method}] {url}"):
            self._attach_request_details(method, url, kwargs)

            try:
                response: Response = self._session.request(method, url, **kwargs)
            except requests.exceptions.RequestException as exc:
                logger.error("Request failed: %s %s - %s", method, url, exc)
                raise

            self._attach_response_details(response)
            return response

    # ------------------------------------------------------------------
    # Allure attachment helpers
    # ------------------------------------------------------------------

    def _attach_request_details(
            self,
            method: str,
            url: str,
            kwargs: dict[str, Any],
    ) -> None:
        """
        Attach request metadata to the current Allure step.
        Sanitizes the Authorization header before attaching to avoid
        leaking tokens into report.

        Args:
            method:   HTTP verb string.
            url:      Full resolved URL.
            kwargs:   Request keyword arguments (headersm body, params, etc.)
        """
        # Mask the Authorization header value to protect credentials in reports
        headers = dict(self._session.headers)
        if "Authorization" in headers:
            headers["Authorization"] = "Bearer *** (masked)"

        request_info = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": kwargs.get("params"),
            "body": kwargs.get("json"),
        }

        log_message = f"{method} {url}"
        logger.info("▶️ REQUEST | %s | body=%s", log_message, kwargs.get("json"))

        allure.attach(
            body=json.dumps(request_info, indent=2, ensure_ascii=False),
            name="Request Details",
            attachment_type=allure.attachment_type.JSON,
        )

    def _attach_response_details(self, response: Response) -> None:
        """
        Attach response metadata to the current Allure step.
        Attempts JSON parsing for a clean attachment; falls back to plain text.

        Args:
            response: The request.Response object returned by the server.
        """
        logger.info(
            "◀️ RESPONSE | %s %s | elapsed=%s",
            response.status_code,
            response.url,
            response.elapsed,
        )

        # Try to parse response body as JSON for a readable Allure attachment
        body: Any = None
        try:
            body = response.json()
            body_str = json.dumps(body, indent=2, ensure_ascii=False)
            attachment_type = allure.attachment_type.JSON
        except ValueError:
            # Response body is no JSON (e.g. plain text, HTML error page)
            body_str = response.text
            attachment_type = allure.attachment_type.TEXT

        response_info = {
            "status_code": response.status_code,
            "elapsed_ms": int(response.elapsed.total_seconds() * 1000),
            "url": response.url,
            "body": body,  # type: ignore[possibly-undefined]
        }

        allure.attach(
            body=json.dumps(response_info, indent=2, ensure_ascii=False)
            if attachment_type == allure.attachment_type.JSON
            else body_str,
            name=f"Response [{response.status_code}]",
            attachment_type=attachment_type,
        )
