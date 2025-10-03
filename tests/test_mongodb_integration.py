"""
Integration tests for MongoDB Query Builder

These tests require a MongoDB instance. They can be skipped if MongoDB is not available.
Set MONGODB_URI environment variable to run these tests.
"""

import pytest
import os
from typing import Generator
from datetime import datetime

# Check if pymongo is available
pytest.importorskip("pymongo", reason="pymongo is required for integration tests")

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from mongodb_query_builder import (
    QueryFilter,
    AggregateBuilder,

)


# Get MongoDB URI from environment
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
TEST_DB_NAME = "test_mongodb_query_builder"
TEST_COLLECTION_NAME = "test_collection"


@pytest.fixture(scope="module")
def mongo_client() -> Generator[MongoClient, None, None]:
    """Fixture providing MongoDB client"""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
        # Test connection
        client.server_info()
        yield client
    except Exception as e:
        pytest.skip(f"MongoDB not available: {e}")
    finally:
        if 'client' in locals():
            client.close()


@pytest.fixture(scope="module")
def test_db(mongo_client: MongoClient) -> Database:
    """Fixture providing test database"""
    return mongo_client[TEST_DB_NAME]


@pytest.fixture(scope="function")
def test_collection(test_db: Database) -> Generator[Collection, None, None]:
    """Fixture providing test collection (cleaned after each test)"""
    collection = test_db[TEST_COLLECTION_NAME]
    yield collection
    # Cleanup
    collection.drop()


@pytest.fixture
def sample_users_data():
    """Fixture providing sample user data"""
    return [
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "age": 28,
            "status": "active",
            "tags": ["python", "mongodb", "docker"],
            "level": "senior",
            "salary": 85000,
            "created_at": datetime(2023, 1, 15)
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "age": 35,
            "status": "active",
            "tags": ["java", "spring", "kubernetes"],
            "level": "senior",
            "salary": 95000,
            "created_at": datetime(2023, 2, 20)
        },
        {
            "name": "Carol Davis",
            "email": "carol@example.com",
            "age": 24,
            "status": "active",
            "tags": ["javascript", "react", "nodejs"],
            "level": "mid",
            "salary": 65000,
            "created_at": datetime(2023, 3, 10)
        },
        {
            "name": "David Wilson",
            "email": "david@example.com",
            "age": 42,
            "status": "inactive",
            "tags": ["python", "django"],
            "level": "senior",
            "salary": 90000,
            "created_at": datetime(2023, 4, 5)
        },
        {
            "name": "Eve Martinez",
            "email": "eve@example.com",
            "age": 26,
            "status": "active",
            "tags": ["python", "fastapi", "postgresql"],
            "level": "mid",
            "salary": 70000,
            "created_at": datetime(2023, 5, 12)
        }
    ]


@pytest.mark.integration
class TestQueryFilterIntegration:
    """Integration tests for QueryFilter with real MongoDB"""
    
    def test_simple_equals_query(self, test_collection, sample_users_data):
        """Test simple equality query"""
        test_collection.insert_many(sample_users_data)
        
        query = QueryFilter().field("status").equals("active")
        results = list(test_collection.find(query.build()))
        
        assert len(results) == 4
        assert all(doc["status"] == "active" for doc in results)
    
    def test_greater_than_query(self, test_collection, sample_users_data):
        """Test greater than query"""
        test_collection.insert_many(sample_users_data)
        
        query = QueryFilter().field("age").greater_than(30)
        results = list(test_collection.find(query.build()))
        
        assert len(results) == 2
        assert all(doc["age"] > 30 for doc in results)
    
    def test_between_query(self, test_collection, sample_users_data):
        """Test between query"""
        test_collection.insert_many(sample_users_data)
        
        query = QueryFilter().field("salary").between(70000, 90000)
        results = list(test_collection.find(query.build()))
        
        assert len(results) == 3
        assert all(70000 <= doc["salary"] <= 90000 for doc in results)
    
    def test_in_list_query(self, test_collection, sample_users_data):
        """Test in list query"""
        test_collection.insert_many(sample_users_data)
        
        query = QueryFilter().field("level").in_list(["senior", "mid"])
        results = list(test_collection.find(query.build()))
        
        assert len(results) == 5
    
    def test_contains_query(self, test_collection, sample_users_data):
        """Test string contains query"""
        test_collection.insert_many(sample_users_data)
        
        query = QueryFilter().field("name").contains("son", case_sensitive=False)
        results = list(test_collection.find(query.build()))
        
        assert len(results) == 2  # Alice Johnson, David Wilson
    
    def test_array_contains_query(self, test_collection, sample_users_data):
        """Test array contains query"""
        test_collection.insert_many(sample_users_data)
        
        query = QueryFilter().field("tags").array_contains("python")
        results = list(test_collection.find(query.build()))
        
        assert len(results) == 3
        assert all("python" in doc["tags"] for doc in results)
    
    def test_complex_and_query(self, test_collection, sample_users_data):
        """Test complex AND query"""
        test_collection.insert_many(sample_users_data)
        
        query = (
            QueryFilter()
            .field("status").equals("active")
            .field("age").greater_than(25)
            .field("level").equals("senior")
        )
        results = list(test_collection.find(query.build()))
        
        assert len(results) == 2
        assert all(doc["status"] == "active" for doc in results)
        assert all(doc["age"] > 25 for doc in results)
        assert all(doc["level"] == "senior" for doc in results)
    
    def test_or_query(self, test_collection, sample_users_data):
        """Test OR query"""
        test_collection.insert_many(sample_users_data)
        
        query = QueryFilter().any_of([
            QueryFilter().field("name").starts_with("Alice"),
            QueryFilter().field("name").starts_with("Bob")
        ])
        results = list(test_collection.find(query.build()))
        
        assert len(results) == 2


@pytest.mark.integration
class TestAggregateBuilderIntegration:
    """Integration tests for AggregateBuilder with real MongoDB"""
    
    def test_match_and_count(self, test_collection, sample_users_data):
        """Test match and count"""
        test_collection.insert_many(sample_users_data)
        
        pipeline = (
            AggregateBuilder()
            .match(QueryFilter().field("status").equals("active"))
            .count("total")
        ).build()
        
        results = list(test_collection.aggregate(pipeline))
        assert len(results) == 1
        assert results[0]["total"] == 4
    
    def test_group_by_field(self, test_collection, sample_users_data):
        """Test group by field"""
        test_collection.insert_many(sample_users_data)
        
        pipeline = (
            AggregateBuilder()
            .group(by="$level", count={"$sum": 1}, avg_salary={"$avg": "$salary"})
            .sort("count", ascending=False)
        ).build()
        
        results = list(test_collection.aggregate(pipeline))
        assert len(results) == 2  # senior and mid
        
        # Check results
        levels = {doc["_id"]: doc for doc in results}
        assert "senior" in levels
        assert "mid" in levels
        assert levels["senior"]["count"] == 3
        assert levels["mid"]["count"] == 2
    
    def test_match_project_limit(self, test_collection, sample_users_data):
        """Test match, project, and limit"""
        test_collection.insert_many(sample_users_data)
        
        pipeline = (
            AggregateBuilder()
            .match({"status": "active"})
            .project(name=1, email=1, age=1)
            .sort("age", ascending=True)
            .limit(2)
        ).build()
        
        results = list(test_collection.aggregate(pipeline))
        assert len(results) == 2
        assert all("name" in doc for doc in results)
        assert all("salary" not in doc for doc in results)  # Not projected
    
    def test_unwind_array(self, test_collection, sample_users_data):
        """Test unwind array field"""
        test_collection.insert_many(sample_users_data)
        
        pipeline = (
            AggregateBuilder()
            .match({"name": "Alice Johnson"})
            .unwind("tags")
        ).build()
        
        results = list(test_collection.aggregate(pipeline))
        assert len(results) == 3  # Alice has 3 tags
        assert all("tags" in doc for doc in results)
        assert all(isinstance(doc["tags"], str) for doc in results)
    
    def test_add_fields(self, test_collection, sample_users_data):
        """Test add computed fields"""
        test_collection.insert_many(sample_users_data)
        
        pipeline = (
            AggregateBuilder()
            .add_fields(
                salary_category={"$cond": [
                    {"$gte": ["$salary", 80000]},
                    "high",
                    "medium"
                ]}
            )
            .project(name=1, salary=1, salary_category=1)
        ).build()
        
        results = list(test_collection.aggregate(pipeline))
        assert len(results) == 5
        assert all("salary_category" in doc for doc in results)
    
    def test_bucket(self, test_collection, sample_users_data):
        """Test bucket aggregation"""
        test_collection.insert_many(sample_users_data)
        
        pipeline = (
            AggregateBuilder()
            .bucket(
                group_by="$age",
                boundaries=[20, 30, 40, 50],
                output={"count": {"$sum": 1}, "names": {"$push": "$name"}}
            )
        ).build()
        
        results = list(test_collection.aggregate(pipeline))
        assert len(results) >= 2  # At least 2 buckets
    
    def test_facet(self, test_collection, sample_users_data):
        """Test facet aggregation"""
        test_collection.insert_many(sample_users_data)
        
        pipeline = (
            AggregateBuilder()
            .facet(
                by_level=[
                    {"$group": {"_id": "$level", "count": {"$sum": 1}}}
                ],
                by_status=[
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                ]
            )
        ).build()
        
        results = list(test_collection.aggregate(pipeline))
        assert len(results) == 1
        assert "by_level" in results[0]
        assert "by_status" in results[0]


@pytest.mark.integration
class TestComplexIntegration:
    """Complex integration tests"""
    
    def test_lookup_with_related_collections(self, test_db):
        """Test lookup between collections"""
        users = test_db["users"]
        orders = test_db["orders"]
        
        try:
            # Insert test data
            user_ids = users.insert_many([
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"}
            ]).inserted_ids
            
            orders.insert_many([
                {"user_id": user_ids[0], "total": 100, "status": "completed"},
                {"user_id": user_ids[0], "total": 150, "status": "completed"},
                {"user_id": user_ids[1], "total": 200, "status": "pending"}
            ])
            
            # Query with lookup
            pipeline = (
                AggregateBuilder()
                .lookup("orders", "_id", "user_id", "orders")
                .unwind("orders")
                .group(
                    by="$name",
                    total_spent={"$sum": "$orders.total"},
                    order_count={"$sum": 1}
                )
            ).build()
            
            results = list(users.aggregate(pipeline))
            assert len(results) == 2
            
            # Find Alice's results
            alice = next(r for r in results if r["_id"] == "Alice")
            assert alice["total_spent"] == 250
            assert alice["order_count"] == 2
            
        finally:
            users.drop()
            orders.drop()
    
    def test_real_world_analytics_pipeline(self, test_collection, sample_users_data):
        """Test real-world analytics pipeline"""
        test_collection.insert_many(sample_users_data)
        
        pipeline = (
            AggregateBuilder()
            .match(QueryFilter().field("status").equals("active"))
            .group(
                by="$level",
                count={"$sum": 1},
                avg_salary={"$avg": "$salary"},
                max_salary={"$max": "$salary"},
                min_salary={"$min": "$salary"}
            )
            .sort("avg_salary", ascending=False)
            .project(
                level="$_id",
                count=1,
                avg_salary={"$round": ["$avg_salary", 2]},
                max_salary=1,
                min_salary=1,
                _id=0
            )
        ).build()
        
        results = list(test_collection.aggregate(pipeline))
        assert len(results) == 2
        
        # Verify structure
        for result in results:
            assert "level" in result
            assert "count" in result
            assert "avg_salary" in result
            assert "max_salary" in result
            assert "min_salary" in result
            assert "_id" not in result


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Performance and stress tests"""
    
    def test_large_dataset_query(self, test_collection):
        """Test query performance on large dataset"""
        # Insert 1000 documents
        documents = [
            {
                "index": i,
                "value": i * 2,
                "category": f"cat_{i % 10}",
                "active": i % 2 == 0
            }
            for i in range(1000)
        ]
        test_collection.insert_many(documents)
        
        # Query with filtering
        query = (
            QueryFilter()
            .field("active").equals(True)
            .field("value").between(500, 1500)
        )
        results = list(test_collection.find(query.build()))
        
        assert len(results) > 0
        assert all(doc["active"] is True for doc in results)
        assert all(500 <= doc["value"] <= 1500 for doc in results)
    
    def test_complex_aggregation_performance(self, test_collection):
        """Test aggregation performance"""
        # Insert test data
        documents = [
            {
                "category": f"cat_{i % 5}",
                "value": i,
                "tags": [f"tag_{j}" for j in range(i % 3)]
            }
            for i in range(500)
        ]
        test_collection.insert_many(documents)
        
        # Complex aggregation
        pipeline = (
            AggregateBuilder()
            .unwind("tags", preserve_null=True)
            .group(
                by={"category": "$category", "tag": "$tags"},
                count={"$sum": 1},
                total_value={"$sum": "$value"}
            )
            .sort("total_value", ascending=False)
            .limit(10)
        ).build()
        
        results = list(test_collection.aggregate(pipeline))
        assert len(results) <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])