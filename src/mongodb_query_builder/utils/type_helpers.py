"""
Type conversion and helper utilities for mongodb-query-builder.

Provides functions for type checking and conversion.
"""

from typing import Any, List

try:
    from bson import ObjectId

    BSON_AVAILABLE = True
except ImportError:
    BSON_AVAILABLE = False

    # Fallback ObjectId for type hints when bson is not installed
    class ObjectId:  # type: ignore
        """Fallback ObjectId class when bson is not installed."""

        @staticmethod
        def is_valid(oid: Any) -> bool:
            """Check if string is valid ObjectId format."""
            if not isinstance(oid, str):
                return False
            if len(oid) != 24:
                return False
            try:
                int(oid, 16)
                return True
            except ValueError:
                return False


def auto_convert_objectid(value: Any) -> Any:
    """
    Automatically convert valid ObjectId strings to ObjectId instances.

    Args:
        value: Value to potentially convert

    Returns:
        ObjectId if value is valid ObjectId string, otherwise original value
    """
    if not BSON_AVAILABLE:
        return value

    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    return value


def auto_convert_objectid_list(values: List[Any]) -> List[Any]:
    """
    Automatically convert valid ObjectId strings in a list to ObjectId instances.

    Args:
        values: List of values to potentially convert

    Returns:
        List with ObjectId strings converted to ObjectId instances
    """
    if not BSON_AVAILABLE or not values:
        return values

    if isinstance(values[0], str) and ObjectId.is_valid(values[0]):
        return [ObjectId(v) if isinstance(v, str) else v for v in values]
    return values


def is_objectid(value: Any) -> bool:
    """
    Check if a value is an ObjectId instance.

    Args:
        value: Value to check

    Returns:
        True if value is an ObjectId instance
    """
    if not BSON_AVAILABLE:
        return False
    return isinstance(value, ObjectId)


def is_valid_objectid_string(value: Any) -> bool:
    """
    Check if a value is a valid ObjectId string.

    Args:
        value: Value to check

    Returns:
        True if value is a valid ObjectId string
    """
    if not isinstance(value, str):
        return False
    return ObjectId.is_valid(value)


__all__ = [
    "ObjectId",
    "BSON_AVAILABLE",
    "auto_convert_objectid",
    "auto_convert_objectid_list",
    "is_objectid",
    "is_valid_objectid_string",
]
