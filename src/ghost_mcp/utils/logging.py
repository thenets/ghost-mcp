"""Logging utilities for Ghost MCP server."""

import logging
import sys
import uuid
from typing import Any, Dict, Optional

import structlog
from structlog.typing import Processor

from ..config import config


def add_request_id(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add request ID to log events."""
    if "request_id" not in event_dict:
        event_dict["request_id"] = str(uuid.uuid4())
    return event_dict


def setup_logging() -> None:
    """Set up structured logging for the application."""
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if config.logging.request_id:
        processors.append(add_request_id)

    if config.logging.structured:
        processors.extend([
            structlog.processors.JSONRenderer()
        ])
    else:
        processors.extend([
            structlog.dev.ConsoleRenderer()
        ])

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, config.logging.level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, config.logging.level.upper()),
    )


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """Get a logger instance."""
    return structlog.get_logger(name)