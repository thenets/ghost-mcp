"""Retry utilities with exponential backoff."""

import asyncio
import time
from typing import Any, Awaitable, Callable, Optional, TypeVar

from pydantic import BaseModel

from ..types.errors import NetworkError, AuthenticationError, GhostApiError, ValidationError
from .logging import get_logger

T = TypeVar("T")
logger = get_logger(__name__)


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 10.0
    exponential_base: float = 2.0
    jitter: bool = True


def _should_retry(exception: Exception) -> bool:
    """Determine if an exception should trigger a retry.

    Only retry transient network errors, not client errors or authentication issues.
    """
    # Retry network errors (connection issues, timeouts)
    if isinstance(exception, NetworkError):
        return True

    # Don't retry authentication errors - these need manual intervention
    if isinstance(exception, AuthenticationError):
        return False

    # Don't retry validation errors - the request is malformed
    if isinstance(exception, ValidationError):
        return False

    # For Ghost API errors, only retry 5xx server errors, not 4xx client errors
    if isinstance(exception, GhostApiError):
        # Check if the error context indicates a server error (5xx)
        if exception.context and "HTTP 5" in exception.context:
            return True
        # Check if it's a rate limiting error (429) - should be retried
        if exception.context and "HTTP 429" in exception.context:
            return True
        # All other Ghost API errors (4xx) should not be retried
        return False

    # For unknown exceptions, be conservative and retry (could be network issues)
    # but log a warning so we can identify what should/shouldn't be retried
    logger.warning(
        "Unknown exception type encountered in retry logic",
        exception_type=type(exception).__name__,
        exception=str(exception)
    )
    return True


async def with_retry(
    operation: Callable[[], Awaitable[T]],
    config: Optional[RetryConfig] = None,
    request_id: Optional[str] = None,
) -> T:
    """Execute operation with exponential backoff retry logic."""
    if config is None:
        config = RetryConfig()

    last_exception: Optional[Exception] = None

    for attempt in range(config.max_retries + 1):
        try:
            return await operation()
        except Exception as e:
            last_exception = e

            # Check if this exception should trigger a retry
            if not _should_retry(e):
                logger.debug(
                    "Exception not suitable for retry, failing immediately",
                    attempt=attempt,
                    exception_type=type(e).__name__,
                    error=str(e),
                    request_id=request_id,
                )
                break

            if attempt == config.max_retries:
                logger.error(
                    "Operation failed after all retries",
                    attempt=attempt,
                    max_retries=config.max_retries,
                    error=str(e),
                    request_id=request_id,
                )
                break

            # Calculate delay with exponential backoff
            delay = min(
                config.base_delay * (config.exponential_base ** attempt),
                config.max_delay
            )

            # Add jitter to prevent thundering herd
            if config.jitter:
                import random
                delay = delay * (0.5 + random.random() * 0.5)

            logger.warning(
                "Operation failed, retrying",
                attempt=attempt,
                delay=delay,
                error=str(e),
                request_id=request_id,
            )

            await asyncio.sleep(delay)

    # Re-raise the last exception
    if last_exception:
        raise last_exception

    raise NetworkError("Retry logic failed unexpectedly", request_id=request_id)