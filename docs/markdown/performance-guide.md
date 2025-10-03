# Performance Guide

This guide provides best practices and optimization techniques for using MongoDB Query Builder efficiently.

## Query Performance Fundamentals

### 1. Use Indexes Effectively

MongoDB queries perform best when they can use indexes. Design your queries to take advantage of existing indexes.

#### Single Field Index

```python
# Efficient: Uses index on status field
query = QueryFilter()
    .field("status").equals("active")
    .build()

# Create index in MongoDB:
# db.collection.createIndex({"status": 1})
```

#### Compound Index

```python
# Efficient: Uses compound index
query = QueryFilter()
    .field("status").equals("active")
    .field("created_date").greater_than(datetime(2024, 1, 1))
    .field("category").equals("electronics")
    .build()

# Create compound index (order matters!):
# db.collection.createIndex({"status": 1, "created_date": -1, "category": 1})
```

### 2. Filter Early in Pipelines

Place `$match` stages as early as possible in aggregation pipelines to reduce the number of documents processed.

```python
# Good: Filter early
pipeline = AggregateBuilder()
    .match(QueryFilter().field("status").equals("active"))  # Filter first
    .lookup(
        from_collection="orders",
        local_field="_id",
        foreign_field="userId",
        as_field="orders"
    )
    .unwind("$orders")
    .group(by="$category", total={"$sum": "$orders.amount"})
    .build()

# Bad: Filter late
pipeline = AggregateBuilder()
    .lookup(
        from_collection="orders",
        local_field="_id",
        foreign_field="userId",
        as_field="orders"
    )
    .unwind("$orders")
    .match(QueryFilter().field("status").equals("active"))  # Filter late
    .group(by="$category", total={"$sum": "$orders.amount"})
    .build()
```

### 3. Limit Result Sets

Always limit results when you don't need all documents.

```python
# Good: Limit results
query = QueryFilter()
    .field("category").equals("books")
    .build()

results = collection.find(query).limit(100)

# Or in aggregation
pipeline = AggregateBuilder()
    .match(QueryFilter().field("category").equals("books"))
    .sort("rating", ascending=False)
    .limit(100)
    .build()
```

## Query Optimization Patterns

### 1. Selective Field Projection

Only retrieve fields you need to reduce network transfer and memory usage.

```python
# Good: Select only needed fields
pipeline = AggregateBuilder()
    .match(QueryFilter().field("status").equals("active"))
    .project(
        name=1,
        email=1,
        lastLogin=1,
        _id=0  # Exclude _id if not needed
    )
    .build()

# With PyMongo
results = collection.find(
    query,
    {"name": 1, "email": 1, "lastLogin": 1, "_id": 0}
)
```

### 2. Efficient Range Queries

Use appropriate operators for range queries to maximize index usage.

```python
# Good: Single range with index
query = QueryFilter()
    .field("price").between(100, 500)
    .build()

# Better: If you have a compound index on (category, price)
query = QueryFilter()
    .field("category").equals("electronics")
    .field("price").between(100, 500)
    .build()
```

### 3. Optimize Array Operations

Array operations can be expensive. Use them judiciously.

```python
# Efficient: Single array check
query = QueryFilter()
    .field("tags").array_contains("mongodb")
    .build()

# Less efficient: Multiple array conditions
query = QueryFilter()
    .field("tags").array_contains_all(["mongodb", "python", "nosql"])
    .field("tags").array_size(5)
    .build()

# Consider restructuring data or using aggregation for complex array queries
```

### 4. Smart Logical Operations

Structure logical operations for best performance.

```python
# Good: Most selective condition first
query = QueryFilter()
    .field("accountType").equals("premium")  # Very selective
    .field("status").equals("active")        # Less selective
    .build()

# For OR conditions, put most likely matches first
query = QueryFilter().any_of([
    QueryFilter().field("priority").equals("high"),      # Most common
    QueryFilter().field("escalated").equals(True),       # Less common
    QueryFilter().field("vip_customer").equals(True)     # Rare
]).build()
```

## Aggregation Pipeline Optimization

### 1. Pipeline Stage Ordering

MongoDB can optimize certain stage sequences. Follow these patterns:

```python
# Optimal order for common operations
pipeline = AggregateBuilder()
    # 1. Filter documents
    .match(QueryFilter().field("year").equals(2024))
    
    # 2. Sort (can use index if immediately after match)
    .sort("date", ascending=True)
    
    # 3. Limit (combines with sort for top-k optimization)
    .limit(100)
    
    # 4. Project to reduce document size
    .project(date=1, amount=1, category=1)
    
    # 5. Additional processing
    .group(by="$category", total={"$sum": "$amount"})
    .build()
```

### 2. Minimize Document Modifications

Avoid unnecessary document reshaping in pipelines.

```python
# Bad: Multiple reshaping stages
pipeline = AggregateBuilder()
    .add_fields(temp1={"$multiply": ["$price", "$quantity"]})
    .add_fields(temp2={"$multiply": ["$temp1", 0.9]})
    .add_fields(final={"$round": ["$temp2", 2]})
    .build()

# Good: Single computation stage
pipeline = AggregateBuilder()
    .add_fields(
        final={
            "$round": [
                {"$multiply": [
                    {"$multiply": ["$price", "$quantity"]},
                    0.9
                ]},
                2
            ]
        }
    )
    .build()
```

### 3. Use allowDiskUse for Large Datasets

For aggregations processing large amounts of data:

```python
# Enable disk use for large aggregations
pipeline = AggregateBuilder()
    .match(QueryFilter().field("year").equals(2024))
    .group(by="$customerId", totalSpent={"$sum": "$amount"})
    .sort("totalSpent", ascending=False)
    .build()

# Execute with allowDiskUse
results = collection.aggregate(pipeline, allowDiskUse=True)
```

### 4. Optimize $lookup Operations

Lookups can be expensive. Optimize them carefully.

```python
# Good: Filter before lookup
pipeline = AggregateBuilder()
    .match(QueryFilter().field("status").equals("active"))
    .lookup(
        from_collection="orders",
        local_field="_id",
        foreign_field="userId",
        as_field="orders"
    )
    .build()

# Better: Use pipeline lookup for filtering joined documents
lookup_pipeline = [
    {"$match": {"$expr": {"$eq": ["$userId", "$$user_id"]}}},
    {"$match": {"status": "completed"}},
    {"$limit": 10}
]

pipeline = AggregateBuilder()
    .add_stage({
        "$lookup": {
            "from": "orders",
            "let": {"user_id": "$_id"},
            "pipeline": lookup_pipeline,
            "as": "recent_orders"
        }
    })
    .build()
```

## Atlas Search Performance

### 1. Index Configuration

Configure Atlas Search indexes for optimal performance:

```python
# Use specific paths instead of dynamic mapping
# Index configuration (in Atlas):
{
    "mappings": {
        "fields": {
            "title": {
                "type": "string",
                "analyzer": "lucene.standard"
            },
            "description": {
                "type": "string",
                "analyzer": "lucene.standard"
            },
            "category": {
                "type": "string",
                "analyzer": "lucene.keyword"
            }
        }
    }
}
```

### 2. Efficient Search Queries

```python
# Good: Use compound queries with filters
compound = CompoundBuilder()
compound.must().text("laptop", path="title")
compound.filter().equals("category", "electronics")
compound.filter().range("price", lte=1000)

search = AtlasSearchBuilder()
    .compound(compound)
    .build_stage()

# Bad: Text search without filters
search = AtlasSearchBuilder()
    .text("laptop", path=["title", "description", "specs", "reviews"])
    .build_stage()
```

### 3. Limit Search Fields

Search only necessary fields:

```python
# Good: Specific fields
search = AtlasSearchBuilder()
    .text("mongodb", path=["title", "tags"])
    .build_stage()

# Bad: Searching all fields
search = AtlasSearchBuilder()
    .text("mongodb", path="*")  # Searches all fields
    .build_stage()
```

## Query Patterns to Avoid

### 1. Negation Operators

Negation operators often can't use indexes efficiently:

```python
# Inefficient: Negation
query = QueryFilter()
    .field("status").not_equals("inactive")
    .build()

# Better: Positive match
query = QueryFilter()
    .field("status").in_(["active", "pending", "processing"])
    .build()
```

### 2. Complex Regular Expressions

Avoid unanchored regex patterns:

```python
# Bad: Unanchored regex (full collection scan)
query = QueryFilter()
    .field("email").regex(r".*@example\.com")
    .build()

# Good: Anchored regex (can use index)
query = QueryFilter()
    .field("email").regex(r"^user.*@example\.com$")
    .build()

# Better: Use specific operators
query = QueryFilter()
    .field("email").ends_with("@example.com")
    .build()
```

### 3. Large $in Arrays

Avoid very large arrays in `$in` operators:

```python
# Bad: Huge array
large_list = [str(i) for i in range(10000)]
query = QueryFilter()
    .field("userId").in_(large_list)
    .build()

# Better: Use ranges or multiple queries
query = QueryFilter().any_of([
    QueryFilter().field("userIdPrefix").equals("groupA"),
    QueryFilter().field("userIdPrefix").equals("groupB")
]).build()
```

## Monitoring and Analysis

### 1. Use explain() to Analyze Queries

```python
# Analyze query performance
query = QueryFilter()
    .field("status").equals("active")
    .field("category").equals("electronics")
    .build()

# Get execution stats
explanation = collection.find(query).explain("executionStats")

# Check if index was used
print(explanation["executionStats"]["totalDocsExamined"])
print(explanation["executionStats"]["totalKeysExamined"])
print(explanation["executionStats"]["executionTimeMillis"])
```

### 2. Monitor Slow Queries

Enable MongoDB profiling to identify slow queries:

```python
# Enable profiling for slow queries (> 100ms)
db.setProfilingLevel(1, {"slowms": 100})

# Query the profile collection
slow_queries = db.system.profile.find({
    "millis": {"$gt": 100}
}).sort("millis", -1).limit(10)
```

### 3. Index Usage Statistics

Monitor index usage:

```python
# Get index statistics
index_stats = db.collection.aggregate([
    {"$indexStats": {}}
])

for stat in index_stats:
    print(f"Index: {stat['name']}")
    print(f"Usage: {stat['accesses']['ops']}")
```

## Best Practices Summary

### Do's ✅

1. **Use indexes** - Design queries to leverage indexes
2. **Filter early** - Reduce document count as soon as possible
3. **Project selectively** - Only retrieve needed fields
4. **Limit results** - Use limit() for better performance
5. **Monitor performance** - Use explain() and profiling
6. **Cache results** - Cache frequently accessed, rarely changing data
7. **Batch operations** - Use bulk operations for multiple updates

### Don'ts ❌

1. **Avoid collection scans** - Queries without index usage
2. **Don't over-fetch** - Retrieving more documents than needed
3. **Avoid complex regex** - Unanchored patterns are slow
4. **Limit array operations** - Complex array queries are expensive
5. **Avoid deep nesting** - Deeply nested queries are hard to optimize
6. **Don't ignore cardinality** - High-cardinality fields make better indexes

## Performance Checklist

Before deploying queries to production:

- [ ] Indexes exist for all query patterns
- [ ] Queries tested with explain()
- [ ] Result sets are limited appropriately
- [ ] Only necessary fields are projected
- [ ] Aggregation pipelines filter early
- [ ] No unanchored regex patterns
- [ ] Array operations are minimized
- [ ] Compound indexes match query patterns
- [ ] Monitoring is in place for slow queries
- [ ] Load testing performed on realistic data

## Additional Resources

- [MongoDB Performance Best Practices](https://docs.mongodb.com/manual/administration/analyzing-mongodb-performance/)
- [Index Strategies](https://docs.mongodb.com/manual/applications/indexes/)
- [Aggregation Pipeline Optimization](https://docs.mongodb.com/manual/core/aggregation-pipeline-optimization/)
- [Atlas Search Performance](https://docs.atlas.mongodb.com/atlas-search/performance/)
