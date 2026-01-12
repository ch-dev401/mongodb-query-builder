"""
MongoDB Query Builder

A fluent, type-safe query builder for MongoDB with support for complex queries,
aggregation pipelines, and Atlas Search.

Example Usage:
    >>> from mongodb_query_builder import QueryFilter, AggregateBuilder
    >>> 
    >>> # Simple query
    >>> filter = QueryFilter()\\
    ...     .field("age").greater_than(18)\\
    ...     .field("status").equals("active")
    >>> 
    >>> # Aggregation pipeline
    >>> pipeline = AggregateBuilder()\\
    ...     .match(filter)\\
    ...     .group(by="$category", count={"$sum": 1})\\
    ...     .sort("count", ascending=False)\\
    ...     .build()
"""

from .__version__ import (
    __author__,
    __description__,
    __email__,
    __license__,
    __url__,
    __version__,
)
from .builders import (
    AggregateBuilder,
    AtlasSearchBuilder,
    ClauseBuilder,
    CompoundBuilder,
    IndexField,
    QueryFilter,
    SearchModel,
    SearchQuery,
)
from .exceptions import (
    AggregateBuilderError,
    AtlasSearchError,
    MongoQueryBuilderError,
    OperatorError,
    QueryFilterError,
    ValidationError,
)
from .operators import AggregateOperator, Operator, UpdateOperator

# Expose commonly used utilities
from .utils import ObjectId

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
    "__url__",
    # Main builders
    "QueryFilter",
    "AggregateBuilder",
    "AtlasSearchBuilder",
    "CompoundBuilder",
    "ClauseBuilder",
    # Search models
    "IndexField",
    "SearchModel",
    "SearchQuery",
    # Operators
    "Operator",
    "AggregateOperator",
    "UpdateOperator",
    # Exceptions
    "MongoQueryBuilderError",
    "QueryFilterError",
    "AggregateBuilderError",
    "AtlasSearchError",
    "ValidationError",
    "OperatorError",
    # Utilities
    "ObjectId",
]
