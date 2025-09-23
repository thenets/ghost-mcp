"""Parameter validation utilities."""

import re
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator

from ..types.errors import ValidationError


class PaginationParams(BaseModel):
    """Pagination parameters validation."""
    limit: Optional[int] = Field(None, ge=1, le=50)
    page: Optional[int] = Field(None, ge=1)


class FilterParams(BaseModel):
    """Filter parameters validation."""
    filter: Optional[str] = None
    include: Optional[str] = None
    fields: Optional[str] = None
    order: Optional[str] = None


def validate_pagination_params(params: Dict[str, Any]) -> PaginationParams:
    """Validate pagination parameters."""
    try:
        return PaginationParams(**params)
    except ValueError as e:
        raise ValidationError(f"Invalid pagination parameters: {e}")


def validate_filter_syntax(filter_string: str) -> bool:
    """
    Validate Ghost filter syntax (NQL - Node Query Language).

    Based on contracts/ghost-filtering.md documentation.
    """
    if not filter_string:
        return True

    # Basic validation patterns for common NQL operators
    valid_operators = [
        r"\+",  # AND
        r",",   # OR
        r":",   # EQUALS
        r":-",  # NOT EQUALS
        r":~",  # CONTAINS
        r":-~", # NOT CONTAINS
        r":>",  # GREATER THAN
        r":<",  # LESS THAN
        r":>=", # GREATER THAN OR EQUAL
        r":<=", # LESS THAN OR EQUAL
    ]

    # Check for balanced parentheses
    if filter_string.count('(') != filter_string.count(')'):
        return False

    # Check for balanced square brackets
    if filter_string.count('[') != filter_string.count(']'):
        return False

    # More comprehensive validation would go here
    # For now, we accept most strings as valid
    return True


def validate_id_parameter(id_value: str, parameter_name: str = "id") -> str:
    """Validate ID parameter format."""
    if not id_value or not isinstance(id_value, str):
        raise ValidationError(f"Invalid {parameter_name}: must be a non-empty string")

    if len(id_value.strip()) == 0:
        raise ValidationError(f"Invalid {parameter_name}: cannot be empty or whitespace")

    return id_value.strip()


def validate_slug_parameter(slug: str) -> str:
    """Validate slug parameter format."""
    if not slug or not isinstance(slug, str):
        raise ValidationError("Invalid slug: must be a non-empty string")

    slug = slug.strip()
    if not slug:
        raise ValidationError("Invalid slug: cannot be empty or whitespace")

    # Basic slug validation (alphanumeric, hyphens, underscores)
    if not re.match(r'^[a-zA-Z0-9-_]+$', slug):
        raise ValidationError("Invalid slug: must contain only alphanumeric characters, hyphens, and underscores")

    return slug