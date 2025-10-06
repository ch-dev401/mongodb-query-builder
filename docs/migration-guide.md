# Migration Guide: From Raw MongoDB Queries to Query Builder

This guide helps you convert existing MongoDB queries to use MongoDB Query Builder's fluent API. Each section shows common MongoDB query patterns and their Query Builder equivalents.

## Why Migrate?

- **Type Safety**: Catch errors at development time
- **Readability**: Self-documenting code
- **Maintainability**: Easier to modify and extend
- **IDE Support**: Auto-completion and inline documentation
- **Fewer Bugs**: Validated query construction

## Basic Query Conversions

### Simple Equality

**MongoDB Query:**
```javascript
{ "status": "active" }
```

**Query Builder:**
```python
from mongodb_query_builder import QueryFilter

query = QueryFilter()
    .field("status").equals("active")
    .build()
```

### Multiple Fields

**MongoDB Query:**
```javascript
{
    "status": "active",
    "age": 25,
    "city": "New York"
}
```

**Query Builder:**
```python
query = QueryFilter()
    .field("status").equals("active")
    .field("age").equals(25)
    .field("city").equals("New York")
    .build()
```

## Comparison Operators

### Greater Than

**MongoDB Query:**
```javascript
{ "age": { "$gt": 18 } }
```

**Query Builder:**
```python
query = QueryFilter()
    .field("age").greater_than(18)
    .build()
```

### Range Query

**MongoDB Query:**
```javascript
{ "price": { "$gte": 100, "$lte": 500 } }
```

**Query Builder:**
```python
query = QueryFilter()
    .field("price").between(100, 500)
    .build()
```

### Multiple Comparisons

**MongoDB Query:**
```javascript
{
    "age": { "$gte": 21 },
    "income": { "$gt": 50000 },
    "credit_score": { "$gte": 700 }
}
```

**Query Builder:**
```python
query = QueryFilter()
    .field("age").greater_than_or_equal(21)
    .field("income").greater_than(50000)
    .field("credit_score").greater_than_or_equal(700)
    .build()
```

## Logical Operators

### OR Condition

**MongoDB Query:**
```javascript
{
    "$or": [
        { "status": "active" },
        { "status": "pending" }
    ]
}
```

**Query Builder:**
```python
query = QueryFilter().any_of([
    QueryFilter().field("status").equals("active"),
    QueryFilter().field("status").equals("pending")
]).build()

# Alternative using in_
query = QueryFilter()
    .field("status").in_(["active", "pending"])
    .build()
```

### Complex AND/OR

**MongoDB Query:**
```javascript
{
    "$and": [
        { "type": "premium" },
        {
            "$or": [
                { "credits": { "$gt": 100 } },
                { "subscription": "unlimited" }
            ]
        }
    ]
}
```

**Query Builder:**
```python
query = QueryFilter().all_of([
    QueryFilter().field("type").equals("premium"),
    QueryFilter().any_of([
        QueryFilter().field("credits").greater_than(100),
        QueryFilter().field("subscription").equals("unlimited")
    ])
]).build()
```

## Array Operations

### Array Contains

**MongoDB Query:**
```javascript
{ "tags": "python" }
```

**Query Builder:**
```python
query = QueryFilter()
    .field("tags").array_contains("python")
    .build()
```

### Array Contains All

**MongoDB Query:**
```javascript
{ "skills": { "$all": ["python", "mongodb", "docker"] } }
```

**Query Builder:**
```python
query = QueryFilter()
    .field("skills").array_contains_all(["python", "mongodb", "docker"])
    .build()
```

### Array Size

**MongoDB Query:**
```javascript
{ "items": { "$size": 3 } }
```

**Query Builder:**
```python
query = QueryFilter()
    .field("items").array_size(3)
    .build()
```

## String Operations

### Regex Patterns

**MongoDB Query:**
```javascript
{ "email": { "$regex": "^[a-zA-Z0-9.]+@example\\.com$" } }
```

**Query Builder:**
```python
query = QueryFilter()
    .field("email").regex(r"^[a-zA-Z0-9.]+@example\.com$")
    .build()
```

### Case-Insensitive Contains

**MongoDB Query:**
```javascript
{ "description": { "$regex": "mongodb", "$options": "i" } }
```

**Query Builder:**
```python
query = QueryFilter()
    .field("description").contains("mongodb", case_sensitive=False)
    .build()
```

### Starts With

**MongoDB Query:**
```javascript
{ "username": { "$regex": "^admin" } }
```

**Query Builder:**
```python
query = QueryFilter()
    .field("username").starts_with("admin")
    .build()
```

## Element Operators

### Field Exists

**MongoDB Query:**
```javascript
{ "email": { "$exists": true } }
```

**Query Builder:**
```python
query = QueryFilter()
    .field("email").exists()
    .build()
```

### Type Check

**MongoDB Query:**
```javascript
{ "age": { "$type": "number" } }
```

**Query Builder:**
```python
query = QueryFilter()
    .field("age").type_check("number")
    .build()
```

## Aggregation Pipeline Conversions

### Basic Pipeline

**MongoDB Pipeline:**
```javascript
[
    { "$match": { "status": "active" } },
    { "$group": { 
        "_id": "$category",
        "count": { "$sum": 1 }
    }},
    { "$sort": { "count": -1 } },
    { "$limit": 5 }
]
```

**Query Builder:**
```python
from mongodb_query_builder import AggregateBuilder, QueryFilter

pipeline = AggregateBuilder()
    .match(QueryFilter().field("status").equals("active"))
    .group(by="$category", count={"$sum": 1})
    .sort("count", ascending=False)
    .limit(5)
    .build()
```

### Complex Aggregation

**MongoDB Pipeline:**
```javascript
[
    { "$match": { 
        "created": { "$gte": ISODate("2024-01-01") }
    }},
    { "$lookup": {
        "from": "users",
        "localField": "userId",
        "foreignField": "_id",
        "as": "user"
    }},
    { "$unwind": "$user" },
    { "$group": {
        "_id": {
            "month": { "$month": "$created" },
            "userId": "$userId"
        },
        "totalAmount": { "$sum": "$amount" },
        "orderCount": { "$sum": 1 }
    }},
    { "$project": {
        "month": "$_id.month",
        "userId": "$_id.userId",
        "totalAmount": 1,
        "orderCount": 1,
        "_id": 0
    }}
]
```

**Query Builder:**
```python
from datetime import datetime

pipeline = AggregateBuilder()
    .match(
        QueryFilter()
        .field("created").greater_than_or_equal(datetime(2024, 1, 1))
    )
    .lookup(
        from_collection="users",
        local_field="userId",
        foreign_field="_id",
        as_field="user"
    )
    .unwind("$user")
    .group(
        by={
            "month": {"$month": "$created"},
            "userId": "$userId"
        },
        totalAmount={"$sum": "$amount"},
        orderCount={"$sum": 1}
    )
    .project(
        month="$_id.month",
        userId="$_id.userId",
        totalAmount=1,
        orderCount=1,
        _id=0
    )
    .build()
```

## Atlas Search Conversions

### Basic Text Search

**Atlas Search Query:**
```javascript
{
    "$search": {
        "text": {
            "query": "mongodb python",
            "path": ["title", "description"]
        }
    }
}
```

**Query Builder:**
```python
from mongodb_query_builder import AtlasSearchBuilder

search = AtlasSearchBuilder()
    .text("mongodb python", path=["title", "description"])
    .build_stage()
```

### Compound Search

**Atlas Search Query:**
```javascript
{
    "$search": {
        "compound": {
            "must": [{
                "text": {
                    "query": "developer",
                    "path": "title"
                }
            }],
            "should": [{
                "text": {
                    "query": "senior",
                    "path": "level",
                    "score": { "boost": { "value": 2.0 } }
                }
            }],
            "filter": [{
                "range": {
                    "path": "experience",
                    "gte": 3
                }
            }]
        }
    }
}
```

**Query Builder:**
```python
from mongodb_query_builder import AtlasSearchBuilder, CompoundBuilder

compound = CompoundBuilder()
compound.must().text("developer", path="title")
compound.should().text("senior", path="level", score=2.0)
compound.filter().range("experience", gte=3)

search = AtlasSearchBuilder()
    .compound(compound)
    .build_stage()
```

## Real-World Migration Examples

### Example 1: User Query Migration

**Original MongoDB Query:**
```python
# Raw query construction
query = {
    "$and": [
        {"age": {"$gte": 18, "$lte": 65}},
        {"status": "active"},
        {
            "$or": [
                {"role": "premium"},
                {"credits": {"$gt": 100}}
            ]
        },
        {"skills": {"$all": ["python", "mongodb"]}},
        {"email": {"$exists": True}}
    ]
}
```

**Migrated to Query Builder:**
```python
query = QueryFilter()
    .field("age").between(18, 65)
    .field("status").equals("active")
    .any_of([
        QueryFilter().field("role").equals("premium"),
        QueryFilter().field("credits").greater_than(100)
    ])
    .field("skills").array_contains_all(["python", "mongodb"])
    .field("email").exists()
    .build()
```

### Example 2: Analytics Pipeline Migration

**Original MongoDB Pipeline:**
```python
pipeline = [
    {
        "$match": {
            "timestamp": {
                "$gte": start_date,
                "$lt": end_date
            },
            "event_type": {"$in": ["purchase", "upgrade"]}
        }
    },
    {
        "$group": {
            "_id": {
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "event_type": "$event_type"
            },
            "count": {"$sum": 1},
            "revenue": {"$sum": "$amount"}
        }
    },
    {
        "$sort": {"_id.date": 1}
    },
    {
        "$facet": {
            "daily_summary": [
                {"$group": {
                    "_id": "$_id.date",
                    "total_events": {"$sum": "$count"},
                    "total_revenue": {"$sum": "$revenue"}
                }}
            ],
            "event_breakdown": [
                {"$group": {
                    "_id": "$_id.event_type",
                    "total_count": {"$sum": "$count"},
                    "total_revenue": {"$sum": "$revenue"}
                }}
            ]
        }
    }
]
```

**Migrated to Query Builder:**
```python
pipeline = AggregateBuilder()
    .match(
        QueryFilter()
        .field("timestamp").between(start_date, end_date)
        .field("event_type").in_(["purchase", "upgrade"])
    )
    .group(
        by={
            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "event_type": "$event_type"
        },
        count={"$sum": 1},
        revenue={"$sum": "$amount"}
    )
    .sort("_id.date", ascending=True)
    .facet(
        daily_summary=[
            {"$group": {
                "_id": "$_id.date",
                "total_events": {"$sum": "$count"},
                "total_revenue": {"$sum": "$revenue"}
            }}
        ],
        event_breakdown=[
            {"$group": {
                "_id": "$_id.event_type",
                "total_count": {"$sum": "$count"},
                "total_revenue": {"$sum": "$revenue"}
            }}
        ]
    )
    .build()
```

## Migration Best Practices

### 1. Start with Simple Queries

Begin by migrating your simplest queries first to get familiar with the API:

```python
# Start with basic queries
old_query = {"status": "active", "verified": True}
new_query = QueryFilter()
    .field("status").equals("active")
    .field("verified").equals(True)
    .build()
```

### 2. Create Helper Functions

Build reusable functions for common query patterns:

```python
def date_range_filter(field, start, end):
    """Create a date range filter."""
    return QueryFilter().field(field).between(start, end)

def active_items_filter():
    """Filter for active items."""
    return QueryFilter()
        .field("status").equals("active")
        .field("deleted").equals(False)
```

### 3. Test Incrementally

Compare outputs during migration:

```python
def test_query_migration():
    # Original query
    old_query = {"age": {"$gte": 18}, "status": "active"}
    
    # New query
    new_query = QueryFilter()
        .field("age").greater_than_or_equal(18)
        .field("status").equals("active")
        .build()
    
    # Verify they're equivalent
    assert old_query == new_query
```

### 4. Document Complex Migrations

For complex queries, document the conversion:

```python
# Original: Find users with recent activity and high engagement
# Query combines multiple conditions with complex logic
#
# Migration notes:
# - Converted $and to implicit AND (chained fields)
# - Simplified $or using any_of()
# - Used between() for date ranges

query = QueryFilter()
    .field("last_login").between(week_ago, today)
    .field("engagement_score").greater_than(75)
    .any_of([
        QueryFilter().field("posts_count").greater_than(10),
        QueryFilter().field("comments_count").greater_than(50)
    ])
    .build()
```

## Common Pitfalls and Solutions

### Pitfall 1: Forgetting build()

```python
# Wrong - returns QueryFilter object, not dict
query = QueryFilter().field("status").equals("active")

# Correct - returns MongoDB query dict
query = QueryFilter().field("status").equals("active").build()
```

### Pitfall 2: Incorrect Logical Grouping

```python
# MongoDB: { "$or": [ ... ] } at root level
# Wrong:
query = QueryFilter()
    .field("a").equals(1)
    .any_of([...])  # This creates an AND condition

# Correct:
query = QueryFilter().any_of([
    QueryFilter().field("a").equals(1),
    QueryFilter().field("b").equals(2)
]).build()
```

### Pitfall 3: Array Operations

```python
# MongoDB: { "tags": "python" } matches array containing "python"
# This is already handled by array_contains:
query = QueryFilter()
    .field("tags").array_contains("python")
    .build()
```

## Migration Checklist

- [ ] Identify all MongoDB queries in your codebase
- [ ] Start with read queries (find operations)
- [ ] Migrate simple queries first
- [ ] Create helper functions for repeated patterns
- [ ] Test each migration thoroughly
- [ ] Update any query-building utilities
- [ ] Migrate aggregation pipelines
- [ ] Migrate Atlas Search queries (if applicable)
- [ ] Update documentation and examples
- [ ] Train team on new syntax

## Need Help?

- Check the [API Reference](api/query-filter.md) for detailed method documentation
- Browse [Tutorials](tutorials/01-basic-queries.md) for step-by-step examples
- See the [Troubleshooting Guide](troubleshooting.md) for common issues
- Ask questions in [GitHub Discussions](https://github.com/ch-dev401/mongodb-query-builder/discussions)
