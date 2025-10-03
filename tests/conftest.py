"""
Pytest configuration and shared fixtures
"""

from datetime import datetime
from typing import Any, Dict, List

import pytest
from bson import ObjectId

# Import builders for testing
from mongodb_query_builder import AggregateBuilder, AtlasSearchBuilder, CompoundBuilder, QueryFilter

# ============================================================================
# BASIC FIXTURES
# ============================================================================


@pytest.fixture
def sample_objectid() -> ObjectId:
    """Fixture providing a sample ObjectId"""
    return ObjectId("507f1f77bcf86cd799439011")


@pytest.fixture
def sample_objectids() -> List[ObjectId]:
    """Fixture providing multiple sample ObjectIds"""
    return [
        ObjectId("507f1f77bcf86cd799439011"),
        ObjectId("507f1f77bcf86cd799439012"),
        ObjectId("507f1f77bcf86cd799439013"),
    ]


@pytest.fixture
def sample_datetime() -> datetime:
    """Fixture providing a sample datetime"""
    return datetime(2024, 1, 1, 12, 0, 0)


@pytest.fixture
def sample_date_range() -> Dict[str, datetime]:
    """Fixture providing a date range"""
    return {
        "start": datetime(2024, 1, 1),
        "end": datetime(2024, 12, 31),
    }


# ============================================================================
# QUERY FILTER FIXTURES
# ============================================================================


@pytest.fixture
def empty_query_filter() -> QueryFilter:
    """Fixture providing an empty QueryFilter"""
    return QueryFilter()


@pytest.fixture
def simple_query_filter() -> QueryFilter:
    """Fixture providing a simple QueryFilter with one condition"""
    return QueryFilter().field("status").equals("active")


@pytest.fixture
def complex_query_filter() -> QueryFilter:
    """Fixture providing a complex QueryFilter with multiple conditions"""
    return (
        QueryFilter()
        .field("age")
        .between(18, 65)
        .field("status")
        .equals("active")
        .field("email")
        .exists(True)
    )


# ============================================================================
# AGGREGATE BUILDER FIXTURES
# ============================================================================


@pytest.fixture
def empty_aggregate_builder() -> AggregateBuilder:
    """Fixture providing an empty AggregateBuilder"""
    return AggregateBuilder()


@pytest.fixture
def simple_aggregate_builder() -> AggregateBuilder:
    """Fixture providing a simple aggregation pipeline"""
    return (
        AggregateBuilder()
        .match(QueryFilter().field("status").equals("active"))
        .group(by="$category", count={"$sum": 1})
        .sort("count", ascending=False)
    )


@pytest.fixture
def complex_aggregate_builder() -> AggregateBuilder:
    """Fixture providing a complex aggregation pipeline"""
    return (
        AggregateBuilder()
        .match(QueryFilter().field("age").greater_than(18))
        .lookup("orders", "_id", "user_id", "user_orders")
        .unwind("user_orders")
        .group(by="$_id", total={"$sum": "$user_orders.amount"})
        .sort("total", ascending=False)
        .limit(10)
    )


# ============================================================================
# ATLAS SEARCH FIXTURES
# ============================================================================


@pytest.fixture
def empty_atlas_search_builder() -> AtlasSearchBuilder:
    """Fixture providing an empty AtlasSearchBuilder"""
    return AtlasSearchBuilder()


@pytest.fixture
def simple_atlas_search_builder() -> AtlasSearchBuilder:
    """Fixture providing a simple Atlas search query"""
    return AtlasSearchBuilder().text("python", path="skills")


@pytest.fixture
def empty_compound_builder() -> CompoundBuilder:
    """Fixture providing an empty CompoundBuilder"""
    return CompoundBuilder()


@pytest.fixture
def simple_compound_builder() -> CompoundBuilder:
    """Fixture providing a simple compound query"""
    compound = CompoundBuilder()
    compound.must().text("python", path="skills")
    compound.should().text("senior", path="level")
    return compound


@pytest.fixture
def complex_compound_builder() -> CompoundBuilder:
    """Fixture providing a complex compound query"""
    compound = CompoundBuilder()
    compound.must().text("python", path="skills")
    compound.should().text("senior", path="level", score=2.0)
    compound.filter().range("experience", gte=3)
    compound.must_not().equals("status", "inactive")
    return compound


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================


@pytest.fixture
def sample_user_document() -> Dict[str, Any]:
    """Fixture providing a sample user document"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "status": "active",
        "tags": ["python", "mongodb"],
        "created_at": datetime(2024, 1, 1),
    }


@pytest.fixture
def sample_user_documents() -> List[Dict[str, Any]]:
    """Fixture providing multiple sample user documents"""
    return [
        {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30,
            "status": "active",
            "tags": ["python", "mongodb"],
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439012"),
            "name": "Jane Smith",
            "email": "jane@example.com",
            "age": 25,
            "status": "active",
            "tags": ["javascript", "react"],
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439013"),
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "age": 35,
            "status": "inactive",
            "tags": ["java", "spring"],
        },
    ]


@pytest.fixture
def sample_order_document() -> Dict[str, Any]:
    """Fixture providing a sample order document"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439021"),
        "user_id": ObjectId("507f1f77bcf86cd799439011"),
        "items": [
            {"product": "laptop", "price": 1200, "quantity": 1},
            {"product": "mouse", "price": 25, "quantity": 2},
        ],
        "total": 1250,
        "status": "completed",
        "created_at": datetime(2024, 1, 15),
    }


# ============================================================================
# EXPECTED RESULTS FIXTURES
# ============================================================================


@pytest.fixture
def expected_simple_query() -> Dict[str, Any]:
    """Expected result for a simple query"""
    return {"status": "active"}


@pytest.fixture
def expected_range_query() -> Dict[str, Any]:
    """Expected result for a range query"""
    return {"age": {"$gte": 18, "$lte": 65}}


@pytest.fixture
def expected_or_query() -> Dict[str, Any]:
    """Expected result for an OR query"""
    return {"$or": [{"role": "admin"}, {"role": "moderator"}]}


@pytest.fixture
def expected_simple_pipeline() -> List[Dict[str, Any]]:
    """Expected result for a simple aggregation pipeline"""
    return [
        {"$match": {"status": "active"}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]


# ============================================================================
# PYTEST HOOKS
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")


def pytest_collection_modifyitems(config, items):
    """Modify collected test items"""
    # Add unit marker to all tests in unit directory
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
