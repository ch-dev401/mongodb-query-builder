"""
Utility functions package.

Exports validation and type helper utilities.
"""

from .type_helpers import (
    BSON_AVAILABLE,
    ObjectId,
    auto_convert_objectid,
    auto_convert_objectid_list,
    is_objectid,
    is_valid_objectid_string,
)
from .validation import (
    ensure_dollar_prefix,
    remove_dollar_prefix,
    validate_at_least_one,
    validate_dict_not_empty,
    validate_field_name,
    validate_non_empty_list,
    validate_positive_number,
    validate_string_not_empty,
)

__all__ = [
    # Type helpers
    "ObjectId",
    "BSON_AVAILABLE",
    "auto_convert_objectid",
    "auto_convert_objectid_list",
    "is_objectid",
    "is_valid_objectid_string",
    # Validation
    "validate_field_name",
    "validate_non_empty_list",
    "validate_positive_number",
    "validate_dict_not_empty",
    "validate_string_not_empty",
    "validate_at_least_one",
    "ensure_dollar_prefix",
    "remove_dollar_prefix",
]