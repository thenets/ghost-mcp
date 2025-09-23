"""Ghost API client with unified interface for Content and Admin APIs."""

import uuid
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import httpx
from httpx import Response

from .auth import AdminAuth, ContentAuth
from .config import config
from .types.errors import AuthenticationError, GhostApiError, NetworkError
from .types.ghost import GhostApiResponse, GhostErrorResponse
from .utils.logging import get_logger
from .utils.retry import RetryConfig, with_retry

logger = get_logger(__name__)


class GhostClient:
    """Unified Ghost API client for both Content and Admin APIs."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        content_api_key: Optional[str] = None,
        admin_api_key: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """Initialize Ghost client with optional configuration overrides."""
        self.base_url = base_url or str(config.ghost.url)
        self.timeout = timeout or config.ghost.timeout

        # Ensure base URL has proper format
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        # Initialize authentication handlers
        self.content_auth = ContentAuth(content_api_key)
        self.admin_auth = AdminAuth(admin_api_key)

        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=100),
        )

        # Retry configuration
        self.retry_config = RetryConfig(
            max_retries=config.ghost.max_retries,
            base_delay=1.0,
            exponential_base=config.ghost.retry_backoff_factor,
        )

    async def __aenter__(self) -> "GhostClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    def _build_url(self, endpoint: str, api_type: str = "content") -> str:
        """Build full URL for API endpoint."""
        api_base = f"ghost/api/{api_type}/"
        return urljoin(self.base_url, api_base + endpoint)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        api_type: str = "content",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Ghost API with error handling and retries."""
        if request_id is None:
            request_id = str(uuid.uuid4())

        url = self._build_url(endpoint, api_type)
        headers = {"User-Agent": "Ghost-MCP/0.1.0"}

        # Add authentication
        if api_type == "content":
            if not self.content_auth.is_configured():
                raise AuthenticationError(
                    "Content API key not configured",
                    request_id=request_id,
                )
            if params is None:
                params = {}
            params.update(self.content_auth.get_auth_params(request_id))

        elif api_type == "admin":
            if not self.admin_auth.is_configured():
                raise AuthenticationError(
                    "Admin API key not configured",
                    request_id=request_id,
                )
            headers.update(self.admin_auth.get_auth_headers(request_id))

        # Prepare request data
        request_kwargs: Dict[str, Any] = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
        }

        if json_data is not None:
            request_kwargs["json"] = json_data
        if files is not None:
            request_kwargs["files"] = files

        logger.info(
            "Making Ghost API request",
            method=method,
            url=url,
            api_type=api_type,
            request_id=request_id,
        )

        async def _request() -> Dict[str, Any]:
            try:
                response: Response = await self.client.request(**request_kwargs)
                return await self._handle_response(response, request_id)
            except httpx.TimeoutException as e:
                raise NetworkError(
                    f"Request timeout: {e}",
                    context=f"Timeout after {self.timeout}s",
                    request_id=request_id,
                ) from e
            except httpx.ConnectError as e:
                raise NetworkError(
                    f"Connection error: {e}",
                    context=f"Failed to connect to {url}",
                    request_id=request_id,
                ) from e
            except httpx.HTTPError as e:
                raise NetworkError(
                    f"HTTP error: {e}",
                    context=f"Request to {url} failed",
                    request_id=request_id,
                ) from e

        return await with_retry(_request, self.retry_config, request_id)

    async def _handle_response(self, response: Response, request_id: str) -> Dict[str, Any]:
        """Handle HTTP response and convert to appropriate format or raise errors."""
        logger.debug(
            "Received Ghost API response",
            status_code=response.status_code,
            headers=dict(response.headers),
            request_id=request_id,
        )

        # Check for successful response
        if response.status_code < 400:
            try:
                data = response.json()
                logger.debug("Successfully parsed response JSON", request_id=request_id)
                return data
            except Exception as e:
                raise GhostApiError(
                    f"Failed to parse response JSON: {e}",
                    context="Invalid JSON response from Ghost API",
                    request_id=request_id,
                ) from e

        # Handle error responses
        try:
            error_data = response.json()
            error_response = GhostErrorResponse(**error_data)

            # Get first error for primary error info
            first_error = error_response.errors[0] if error_response.errors else None
            error_message = first_error.message if first_error else "Unknown Ghost API error"
            error_code = first_error.code if first_error else None

            raise GhostApiError(
                error_message,
                code=error_code,
                context=f"HTTP {response.status_code}",
                request_id=request_id,
            )

        except Exception as e:
            if isinstance(e, GhostApiError):
                raise

            # Fallback for non-JSON error responses
            raise GhostApiError(
                f"HTTP {response.status_code}: {response.text}",
                context="Non-JSON error response",
                request_id=request_id,
            ) from e

    # Content API methods
    async def get_posts(
        self,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        filter: Optional[str] = None,
        include: Optional[str] = None,
        fields: Optional[str] = None,
        order: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get posts from Content API."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page
        if filter is not None:
            params["filter"] = filter
        if include is not None:
            params["include"] = include
        if fields is not None:
            params["fields"] = fields
        if order is not None:
            params["order"] = order

        return await self._make_request(
            "GET", "posts/", api_type="content", params=params, request_id=request_id
        )

    async def get_post_by_id(
        self,
        post_id: str,
        include: Optional[str] = None,
        fields: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get single post by ID from Content API."""
        params = {}
        if include is not None:
            params["include"] = include
        if fields is not None:
            params["fields"] = fields

        return await self._make_request(
            "GET", f"posts/{post_id}/", api_type="content", params=params, request_id=request_id
        )

    async def get_post_by_slug(
        self,
        slug: str,
        include: Optional[str] = None,
        fields: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get single post by slug from Content API."""
        params = {}
        if include is not None:
            params["include"] = include
        if fields is not None:
            params["fields"] = fields

        return await self._make_request(
            "GET", f"posts/slug/{slug}/", api_type="content", params=params, request_id=request_id
        )

    # Admin API methods (examples)
    async def create_post(
        self,
        post_data: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create new post via Admin API."""
        return await self._make_request(
            "POST", "posts/", api_type="admin", json_data=post_data, request_id=request_id
        )

    async def update_post(
        self,
        post_id: str,
        post_data: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update existing post via Admin API."""
        return await self._make_request(
            "PUT", f"posts/{post_id}/", api_type="admin", json_data=post_data, request_id=request_id
        )

    async def delete_post(
        self,
        post_id: str,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete post via Admin API."""
        return await self._make_request(
            "DELETE", f"posts/{post_id}/", api_type="admin", request_id=request_id
        )