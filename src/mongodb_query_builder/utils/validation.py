"""
Validation utilities for mongodb-query-builder.

Provides helper functions for input validation and sanitization.
"""

from typing import Any, Dict, List, Optional

from ..exceptions import ValidationError


def validate_field_name(field_name: Optional[str], context: str = "field") -> None:
    """
    Validate that a field name is not empty.

    Args:
        field_name: The field name to validate
        context: Context for error message

    Raises:
        ValidationError: If field name is None or empty
    """
    if not field_name:
        raise ValidationError(f"{context} name cannot be empty")


def validate_non_empty_list(values: List[Any], context: str = "list") -> None:
    """
    Validate that a list is not empty.

    Args:
        values: The list to validate
        context: Context for error message

    Raises:
        ValidationError: If list is empty
    """
    if not values:
        raise ValidationError(f"{context} cannot be empty")


def validate_positive_number(value: int, context: str = "value", allow_zero: bool = False) -> None:
    """
    Validate that a number is positive.

    Args:
        value: The number to validate
        context: Context for error message
        allow_zero: Whether to allow zero

    Raises:
        ValidationError: If number is not positive
    """
    if allow_zero:
        if value < 0:
            raise ValidationError(f"{context} must be non-negative")
    else:
        if value <= 0:
            raise ValidationError(f"{context} must be positive")


def validate_dict_not_empty(value: Dict[str, Any], context: str = "dictionary") -> None:
    """
    Validate that a dictionary is not empty.

    Args:
        value: The dictionary to validate
        context: Context for error message

    Raises:
        ValidationError: If dictionary is empty
    """
    if not value:
        raise ValidationError(f"{context} cannot be empty")


def validate_string_not_empty(value: str, context: str = "string") -> None:
    """
    Validate that a string is not empty.

    Args:
        value: The string to validate
        context: Context for error message

    Raises:
        ValidationError: If string is empty
    """
    if not value or not value.strip():
        raise ValidationError(f"{context} cannot be empty")


def validate_at_least_one(*values: Any, context: str = "At least one value") -> None:
    """
    Validate that at least one value is not None.

    Args:
        *values: Values to check
        context: Context for error message

    Raises:
        ValidationError: If all values are None
    """
    if all(v is None for v in values):
        raise ValidationError(f"{context} must be provided")


def ensure_dollar_prefix(field: str) -> str:
    """
    Ensure a field reference starts with $.

    Args:
        field: The field reference

    Returns:
        Field reference with $ prefix
    """
    return field if field.startswith("$") else f"${field}"


def remove_dollar_prefix(field: str) -> str:
    """
    Remove $ prefix from a field reference.

    Args:
        field: The field reference

    Returns:
        Field reference without $ prefix
    """
    return field[1:] if field.startswith("$") else field


__all__ = [
    "validate_field_name",
    "validate_non_empty_list",
    "validate_positive_number",
    "validate_dict_not_empty",
    "validate_string_not_empty",
    "validate_at_least_one",
    "ensure_dollar_prefix",
    "remove_dollar_prefix",
]
