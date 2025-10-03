"""
MongoDB Query Filter Builder

Provides a fluent interface for building MongoDB query filters with type safety
and validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, overload

from ..exceptions import QueryFilterError
from ..operators import Operator
from ..utils import ObjectId, auto_convert_objectid, auto_convert_objectid_list


class QueryFilter:
    """
    Fluent MongoDB Query Filter Builder
    
    This class provides a chainable interface for building MongoDB query filters
    with type safety and validation.
    
    Examples:
        # Simple equality
        >>> q = QueryFilter().field("name").equals("John")
        >>> q.build()
        {'name': 'John'}
        
        # Comparison
        >>> q = QueryFilter().field("age").greater_than(18)
        >>> q.build()
        {'age': {'$gt': 18}}
        
        # Multiple conditions (AND)
        >>> q = QueryFilter()\\
        ...     .field("age").between(18, 65)\\
        ...     .field("status").equals("active")
        >>> q.build()
        {'age': {'$gte': 18, '$lte': 65}, 'status': 'active'}
        
        # OR conditions
        >>> q = QueryFilter().any_of([
        ...     QueryFilter().field("role").equals("admin"),
        ...     QueryFilter().field("role").equals("moderator")
        ... ])
        >>> q.build()
        {'$or': [{'role': 'admin'}, {'role': 'moderator'}]}
    """

    def __init__(self):
        """Initialize a new QueryFilter"""
        self._filters: Dict[str, Any] = {}
        self._current_field: Optional[str] = None

    def _validate_current_field(self) -> None:
        """Validate that a field has been set"""
        if not self._current_field:
            raise QueryFilterError("No field selected. Call field() before applying a condition.")

    @overload
    def field(self, field_name: str) -> "QueryFilter": ...

    @overload
    def field(self, field_name: str, value: Any) -> "QueryFilter": ...

    def field(self, field_name: str, value: Any = None) -> "QueryFilter":
        """
        Start filtering on a specific field

        Args:
            field_name: The name of the field to filter on
            value: Optional value to directly set (for simple equality)

        Returns:
            Self for chaining

        Examples:
            >>> QueryFilter().field("name").equals("John")
            >>> QueryFilter().field("status", "active")  # Shorthand
        """
        if not field_name:
            raise QueryFilterError("Field name cannot be empty")

        if value is None:
            self._current_field = field_name
        else:
            self._filters[field_name] = auto_convert_objectid(value)
        return self

    def equals(self, value: Any) -> "QueryFilter":
        """
        Equal to value

        Args:
            value: The value to compare against

        Returns:
            Self for chaining
        """
        self._validate_current_field()
        self._filters[self._current_field] = auto_convert_objectid(value)
        return self

    def not_equals(self, value: Any) -> "QueryFilter":
        """
        Not equal to value

        Args:
            value: The value to compare against

        Returns:
            Self for chaining
        """
        self._validate_current_field()
        self._filters[self._current_field] = {Operator.NE: value}
        return self

    def greater_than(self, value: Union[ObjectId, datetime, int, float]) -> "QueryFilter":
        """
        Greater than value

        Args:
            value: The value to compare against

        Returns:
            Self for chaining
        """
        self._validate_current_field()
        self._filters[self._current_field] = {Operator.GT: value}
        return self

    def greater_than_or_equal(self, value: Union[ObjectId, datetime, int, float]) -> "QueryFilter":
        """
        Greater than or equal to value

        Args:
            value: The value to compare against

        Returns:
            Self for chaining
        """
        self._validate_current_field()
        self._filters[self._current_field] = {Operator.GTE: value}
        return self

    def less_than(self, value: Union[ObjectId, datetime, int, float]) -> "QueryFilter":
        """
        Less than value

        Args:
            value: The value to compare against

        Returns:
            Self for chaining
        """
        self._validate_current_field()
        self._filters[self._current_field] = {Operator.LT: value}
        return self

    def less_than_or_equal(self, value: Union[ObjectId, datetime, int, float]) -> "QueryFilter":
        """
        Less than or equal to value

        Args:
            value: The value to compare against

        Returns:
            Self for chaining
        """
        self._validate_current_field()
        self._filters[self._current_field] = {Operator.LTE: value}
        return self

    def between(
        self,
        min_value: Union[ObjectId, datetime, int, float],
        max_value: Union[ObjectId, datetime, int, float],
        inclusive: bool = True,
    ) -> "QueryFilter":
        """
        Value between min and max

        Args:
            min_value: Minimum value
            max_value: Maximum value
            inclusive: Whether to include boundaries (default: True)

        Returns:
            Self for chaining
        """
        self._validate_current_field()

        if inclusive:
            self._filters[self._current_field] = {Operator.GTE: min_value, Operator.LTE: max_value}
        else:
            self._filters[self._current_field] = {Operator.GT: min_value, Operator.LT: max_value}
        return self

    def in_list(self, values: List[Any]) -> "QueryFilter":
        """
        Value in list

        Args:
            values: List of values to match against

        Returns:
            Self for chaining
        """
        self._validate_current_field()

        if not values:
            raise QueryFilterError("Values list cannot be empty for in_list()")

        # Convert ObjectId strings if needed
        values = auto_convert_objectid_list(values)

        self._filters[self._current_field] = {Operator.IN: values}
        return self

    def not_in_list(self, values: List[Any]) -> "QueryFilter":
        """
        Value not in list

        Args:
            values: List of values to exclude

        Returns:
            Self for chaining
        """
        self._validate_current_field()

        if not values:
            raise QueryFilterError("Values list cannot be empty for not_in_list()")

        self._filters[self._current_field] = {Operator.NIN: values}
        return self

    def contains(self, value: str, case_sensitive: bool = False) -> "QueryFilter":
        """
        String contains value (uses regex)

        Args:
            value: The string to search for
            case_sensitive: Whether the search is case-sensitive

        Returns:
            Self for chaining
        """
        self._validate_current_field()

        options = "" if case_sensitive else "i"
        self._filters[self._current_field] = {Operator.REGEX: value, Operator.OPTIONS: options}
        return self

    def starts_with(self, value: str, case_sensitive: bool = False) -> "QueryFilter":
        """
        String starts with value

        Args:
            value: The prefix to search for
            case_sensitive: Whether the search is case-sensitive

        Returns:
            Self for chaining
        """
        self._validate_current_field()

        options = "" if case_sensitive else "i"
        self._filters[self._current_field] = {
            Operator.REGEX: f"^{value}",
            Operator.OPTIONS: options,
        }
        return self

    def ends_with(self, value: str, case_sensitive: bool = False) -> "QueryFilter":
        """
        String ends with value

        Args:
            value: The suffix to search for
            case_sensitive: Whether the search is case-sensitive

        Returns:
            Self for chaining
        """
        self._validate_current_field()

        options = "" if case_sensitive else "i"
        self._filters[self._current_field] = {
            Operator.REGEX: f"{value}$",
            Operator.OPTIONS: options,
        }
        return self

    def regex(self, pattern: str, flags: str = "") -> "QueryFilter":
        """
        Custom regex pattern

        Args:
            pattern: The regex pattern
            flags: Regex flags (e.g., 'i' for case-insensitive)

        Returns:
            Self for chaining
        """
        self._validate_current_field()

        filter_dict = {Operator.REGEX: pattern}
        if flags:
            filter_dict[Operator.OPTIONS] = flags

        self._filters[self._current_field] = filter_dict
        return self

    def exists(self, should_exist: bool = True) -> "QueryFilter":
        """
        Field exists or not

        Args:
            should_exist: Whether the field should exist

        Returns:
            Self for chaining
        """
        self._validate_current_field()
        self._filters[self._current_field] = {Operator.EXISTS: should_exist}
        return self

    def is_null(self) -> "QueryFilter":
        """
        Field is null

        Returns:
            Self for chaining
        """
        self._validate_current_field()
        self._filters[self._current_field] = None
        return self

    def is_not_null(self) -> "QueryFilter":
        """
        Field is not null

        Returns:
            Self for chaining
        """
        self._validate_current_field()
        self._filters[self._current_field] = {Operator.NE: None}
        return self

    def array_contains(self, value: Any) -> "QueryFilter":
        """
        Array contains value

        Args:
            value: The value to search for in the array

        Returns:
            Self for chaining
        """
        self._validate_current_field()
        self._filters[self._current_field] = value
        return self

    def array_contains_all(self, values: List[Any]) -> "QueryFilter":
        """
        Array contains all values

        Args:
            values: List of values that must all be in the array

        Returns:
            Self for chaining
        """
        self._validate_current_field()

        if not values:
            raise QueryFilterError("Values list cannot be empty for array_contains_all()")

        self._filters[self._current_field] = {Operator.ALL: values}
        return self

    def array_size(self, size: int) -> "QueryFilter":
        """
        Array has specific size

        Args:
            size: The required size of the array

        Returns:
            Self for chaining
        """
        self._validate_current_field()

        if size < 0:
            raise QueryFilterError("Array size must be non-negative")

        self._filters[self._current_field] = {Operator.SIZE: size}
        return self

    def elem_match(self, conditions: Union[Dict[str, Any], "QueryFilter"]) -> "QueryFilter":
        """
        Array element matches conditions

        Args:
            conditions: Dictionary of conditions or QueryFilter

        Returns:
            Self for chaining
        """
        self._validate_current_field()

        if isinstance(conditions, QueryFilter):
            conditions = conditions.build()

        self._filters[self._current_field] = {Operator.ELEM_MATCH: conditions}
        return self

    def all_of(self, filters: List["QueryFilter"]) -> "QueryFilter":
        """
        All conditions must match (AND)

        Args:
            filters: List of QueryFilter objects

        Returns:
            Self for chaining
        """
        if not filters:
            raise QueryFilterError("Filters list cannot be empty for all_of()")

        and_conditions = [f.build() for f in filters]
        if self._filters:
            and_conditions.append(self._filters)

        self._filters = {Operator.AND: and_conditions}
        return self

    def any_of(self, filters: List["QueryFilter"]) -> "QueryFilter":
        """
        Any condition can match (OR)

        Args:
            filters: List of QueryFilter objects

        Returns:
            Self for chaining
        """
        if not filters:
            raise QueryFilterError("Filters list cannot be empty for any_of()")

        or_conditions = [f.build() for f in filters]
        if self._filters:
            or_conditions.append(self._filters)

        self._filters = {Operator.OR: or_conditions}
        return self

    def none_of(self, filters: List["QueryFilter"]) -> "QueryFilter":
        """
        None of the conditions should match (NOR)

        Args:
            filters: List of QueryFilter objects

        Returns:
            Self for chaining
        """
        if not filters:
            raise QueryFilterError("Filters list cannot be empty for none_of()")

        nor_conditions = [f.build() for f in filters]
        if self._filters:
            nor_conditions.append(self._filters)

        self._filters = {Operator.NOR: nor_conditions}
        return self

    def not_filter(self, filter_obj: "QueryFilter") -> "QueryFilter":
        """
        Negate a filter

        Args:
            filter_obj: QueryFilter to negate

        Returns:
            Self for chaining
        """
        not_condition = filter_obj.build()
        self._filters = {Operator.NOT: not_condition}
        return self

    def raw(self, filter_dict: Dict[str, Any]) -> "QueryFilter":
        """
        Add raw MongoDB filter

        Args:
            filter_dict: Raw MongoDB filter dictionary

        Returns:
            Self for chaining
        """
        self._filters.update(filter_dict)
        return self

    def text_search(
        self,
        search_text: str,
        language: Optional[str] = None,
        case_sensitive: bool = False,
        diacritic_sensitive: bool = False,
    ) -> "QueryFilter":
        """
        Full text search (requires text index)

        Args:
            search_text: The text to search for
            language: The language for text search
            case_sensitive: Whether search is case-sensitive
            diacritic_sensitive: Whether search is diacritic-sensitive

        Returns:
            Self for chaining
        """
        text_config = {"$search": search_text}

        if language:
            text_config["$language"] = language
        if case_sensitive:
            text_config["$caseSensitive"] = True
        if diacritic_sensitive:
            text_config["$diacriticSensitive"] = True

        self._filters[Operator.TEXT] = text_config
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build the final MongoDB filter

        Returns:
            Dictionary representing the MongoDB filter
        """
        return self._filters

    def __repr__(self):
        return f"QueryFilter({self._filters})"


__all__ = ["QueryFilter"]
