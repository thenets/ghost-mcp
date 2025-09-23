"""Retry utilities with exponential backoff."""

import asyncio
import time
from typing import Any, Awaitable, Callable, Optional, TypeVar

from pydantic import BaseModel

from ..types.errors import NetworkError
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