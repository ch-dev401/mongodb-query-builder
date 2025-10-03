"""
Custom exceptions for mongodb-query-builder.

This module defines all custom exceptions used throughout the library.
"""


class MongoQueryBuilderError(Exception):
    """Base exception for all mongodb-query-builder errors."""

    pass


class QueryFilterError(MongoQueryBuilderError):
    """Exception raised for errors in QueryFilter operations."""

    pass


class AggregateBuilderError(MongoQueryBuilderError):
    """Exception raised for errors in AggregateBuilder operations."""

    pass


class AtlasSearchError(MongoQueryBuilderError):
    """Exception raised for errors in Atlas Search operations."""

    pass


class ValidationError(MongoQueryBuilderError):
    """Exception raised for validation errors."""

    pass


class OperatorError(MongoQueryBuilderError):
    """Exception raised for invalid operator usage."""

    pass


__all__ = [
    "MongoQueryBuilderError",
    "QueryFilterError",
    "AggregateBuilderError",
    "AtlasSearchError",
    "ValidationError",
    "OperatorError",
]
