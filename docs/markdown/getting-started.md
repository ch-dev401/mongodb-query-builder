# Getting Started with MongoDB Query Builder

This guide will help you get up and running with MongoDB Query Builder in just a few minutes.

## Installation

### Basic Installation

Install MongoDB Query Builder using pip:

```bash
pip install mongodb-query-builder
```

### Installation with MongoDB Support

If you want to use the library with pymongo:

```bash
pip install mongodb-query-builder[mongodb]
```

### Development Installation

For development or to run tests:

```bash
git clone https://github.com/ch-dev401/mongodb-query-builder.git
cd mongodb-query-builder
pip install -e ".[dev,test]"
```

### Install from Source as Package

To install the library from source as a regular package (not in development mode):

```bash
# Clone the repository
git clone https://github.com/ch-dev401/mongodb-query-builder.git
cd mongodb-query-builder

# Install as a package
pip install .

# Or with MongoDB support
pip install ".[mongodb]"

# Or build and install using build tools
python -m build
pip install dist/mongodb_query_builder-*.whl
```

### Install from GitHub

You can also install directly from GitHub:

```bash
# Install latest from main branch
pip install git+https://github.com/ch-dev401/mongodb-query-builder.git

# Install a specific version/tag
pip install git+https://github.com/ch-dev401/mongodb-query-builder.git@v1.0.0

# Install a specific branch
pip install git+https://github.com/ch-dev401/mongodb-query-builder.git@develop
```

## Basic Concepts

MongoDB Query Builder provides three main components:

1. **QueryFilter** - Build MongoDB query filters
2. **AggregateBuilder** - Create aggregation pipelines
3. **AtlasSearchBuilder** - Construct Atlas Search queries

All builders follow a fluent interface pattern, allowing you to chain methods for readable query construction.

## Your First Query

Let's start with a simple example:

```python
from mongodb_query_builder import QueryFilter

# Create a simple query
query = QueryFilter()
    .field("age").greater_than(18)
    .field("status").equals("active")
    .build()

print(query)
# Output: {"age": {"$gt": 18}, "status": "active"}
```

## Using with PyMongo

Here's how to use MongoDB Query Builder with PyMongo:

```python
from pymongo import MongoClient
from mongodb_query_builder import QueryFilter

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["users"]

# Build and execute a query
query = QueryFilter()
    .field("age").between(25, 35)
    .field("city").equals("New York")
    .build()

# Find documents
results = collection.find(query)
for doc in results:
    print(doc)
```

## Building Aggregation Pipelines

Aggregation pipelines allow you to process and transform your data:

```python
from mongodb_query_builder import AggregateBuilder, QueryFilter

# Create an aggregation pipeline
pipeline = AggregateBuilder()
    .match(
        QueryFilter()
        .field("status").equals("completed")
        .field("amount").greater_than(100)
    )
    .group(
        by="$category",
        total_amount={"$sum": "$amount"},
        count={"$sum": 1}
    )
    .sort("total_amount", ascending=False)
    .limit(5)
    .build()

# Execute with PyMongo
results = collection.aggregate(pipeline)
for doc in results:
    print(f"{doc['_id']}: ${doc['total_amount']} ({doc['count']} items)")
```

## Working with Complex Queries

### Logical Operators

Combine multiple conditions using logical operators:

```python
from mongodb_query_builder import QueryFilter

# OR condition
query = QueryFilter().any_of([
    QueryFilter().field("role").equals("admin"),
    QueryFilter().field("role").equals("moderator")
]).build()

# AND condition (implicit)
query = QueryFilter()
    .field("age").greater_than(18)
    .field("status").equals("active")
    .build()

# Complex nested conditions
query = QueryFilter().all_of([
    QueryFilter().field("type").equals("premium"),
    QueryFilter().any_of([
        QueryFilter().field("credits").greater_than(100),
        QueryFilter().field("subscription").equals("unlimited")
    ])
]).build()
```

### Array Operations

Work with array fields:

```python
# Check if array contains a value
query = QueryFilter()
    .field("tags").array_contains("python")
    .build()

# Check if array contains all values
query = QueryFilter()
    .field("skills").array_contains_all(["python", "mongodb", "docker"])
    .build()

# Check array size
query = QueryFilter()
    .field("items").array_size(5)
    .build()
```

### String Operations

Perform string matching:

```python
# Starts with
query = QueryFilter()
    .field("name").starts_with("John")
    .build()

# Contains (case-insensitive)
query = QueryFilter()
    .field("description").contains("python")
    .build()

# Regular expression
query = QueryFilter()
    .field("email").regex(r".*@example\.com$")
    .build()
```

## Atlas Search Example

If you're using MongoDB Atlas, you can build search queries:

```python
from mongodb_query_builder import AtlasSearchBuilder

# Simple text search
search = AtlasSearchBuilder()
    .text("python developer", path=["title", "description"])
    .build_stage()

# Search with fuzzy matching
search = AtlasSearchBuilder()
    .text("pythn", path="skills", fuzzy={"maxEdits": 2})
    .build_stage()

# Use in aggregation pipeline
pipeline = [search, {"$limit": 10}]
results = collection.aggregate(pipeline)
```

## Best Practices

### 1. Use Type Hints

Take advantage of type hints for better IDE support:

```python
from mongodb_query_builder import QueryFilter
from typing import Dict, Any

def get_active_users(min_age: int) -> Dict[str, Any]:
    return QueryFilter()
        .field("age").greater_than_or_equal(min_age)
        .field("status").equals("active")
        .build()
```

### 2. Reuse Query Components

Build reusable query components:

```python
# Create reusable filters
def active_users_filter() -> QueryFilter:
    return QueryFilter().field("status").equals("active")

def premium_users_filter() -> QueryFilter:
    return QueryFilter().field("subscription").in_(["premium", "enterprise"])

# Combine filters
query = QueryFilter().all_of([
    active_users_filter(),
    premium_users_filter()
]).build()
```

### 3. Handle Errors Gracefully

MongoDB Query Builder provides specific exceptions:

```python
from mongodb_query_builder import QueryFilter, QueryFilterError

try:
    query = QueryFilter()
        .field("age").greater_than("not a number")  # This will raise an error
        .build()
except QueryFilterError as e:
    print(f"Query construction error: {e}")
```

## Next Steps

Now that you understand the basics:

1. Explore the [API Reference](api/query-filter.md) for detailed method documentation
2. Check out the [Tutorials](tutorials/01-basic-queries.md) for step-by-step guides
3. Browse the [Cookbook](cookbook/user-authentication.md) for real-world examples
4. Read the [Performance Guide](performance-guide.md) for optimization tips

## Quick Reference

Here's a quick reference of common operations:

| Operation | Method | Example |
|-----------|---------|---------|
| Equals | `equals()` | `.field("status").equals("active")` |
| Not equals | `not_equals()` | `.field("status").not_equals("deleted")` |
| Greater than | `greater_than()` | `.field("age").greater_than(18)` |
| Less than | `less_than()` | `.field("price").less_than(100)` |
| Between | `between()` | `.field("age").between(18, 65)` |
| In array | `in_()` | `.field("role").in_(["admin", "user"])` |
| Contains | `array_contains()` | `.field("tags").array_contains("python")` |
| Exists | `exists()` | `.field("email").exists()` |
| Regex | `regex()` | `.field("name").regex("^John")` |

## Getting Help

If you need help:

- Check the [Troubleshooting Guide](troubleshooting.md)
- Search existing [GitHub Issues](https://github.com/ch-dev401/mongodb-query-builder/issues)
- Ask questions in the [Discussions](https://github.com/ch-dev401/mongodb-query-builder/discussions)
- Report bugs via [GitHub Issues](https://github.com/ch-dev401/mongodb-query-builder/issues/new)

Happy querying! 🚀
