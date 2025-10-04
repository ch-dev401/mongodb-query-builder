# MongoDB Query Builder

A fluent, type-safe query builder for MongoDB with support for complex queries, aggregation pipelines, and Atlas Search.

## Features

✨ **Fluent API** - Chain methods for readable query construction  
🔒 **Type-safe** - Full type hints and validation  
📦 **Comprehensive** - Support for queries, aggregations, and Atlas Search  
🎯 **Intuitive** - Pythonic interface for MongoDB operations  
✅ **Well-tested** - Extensive test coverage  
📚 **Well-documented** - Complete API documentation and examples

## Installation

```bash
pip install mongodb-query-builder
```

## Quick Start

### Simple Query

```python
from mongodb_query_builder import QueryFilter

# Build a query filter
query = QueryFilter()\
    .field("age").greater_than(18)\
    .field("status").equals("active")\
    .build()

# Use with pymongo
collection.find(query)
```

### Aggregation Pipeline

```python
from mongodb_query_builder import AggregateBuilder, QueryFilter

# Build aggregation pipeline
pipeline = AggregateBuilder()\
    .match(QueryFilter().field("status").equals("active"))\
    .group(by="$category", count={"$sum": 1}, total={"$sum": "$amount"})\
    .sort("count", ascending=False)\
    .limit(10)\
    .build()

# Use with pymongo
results = collection.aggregate(pipeline)
```

### Atlas Search

```python
from mongodb_query_builder import AtlasSearchBuilder, CompoundBuilder

# Simple text search
search = AtlasSearchBuilder()\
    .text("python developer", path=["title", "description"])\
    .build_stage()

# Complex compound search
compound = CompoundBuilder()
compound.must().text("python", path="skills")
compound.should().text("senior", path="level", score=2.0)
compound.filter().range("experience", gte=3)

search = AtlasSearchBuilder()\
    .compound(compound)\
    .facet("departments", type="string", path="department")\
    .build_stage()

# Use in aggregation
pipeline = [search, {"$limit": 10}]
results = collection.aggregate(pipeline)
```

## Core Components

### QueryFilter

Build MongoDB query filters with a fluent interface:

```python
from mongodb_query_builder import QueryFilter

# Comparison operators
q = QueryFilter().field("age").greater_than(18)
q = QueryFilter().field("price").between(10, 100)

# String operations
q = QueryFilter().field("name").starts_with("John")
q = QueryFilter().field("email").contains("@example.com")

# Array operations
q = QueryFilter().field("tags").array_contains("python")
q = QueryFilter().field("skills").array_contains_all(["python", "mongodb"])

# Logical operators
q = QueryFilter().any_of([
    QueryFilter().field("role").equals("admin"),
    QueryFilter().field("role").equals("moderator")
])
```

### AggregateBuilder

Build aggregation pipelines:

```python
from mongodb_query_builder import AggregateBuilder

pipeline = AggregateBuilder()\
    .match(QueryFilter().field("status").equals("active"))\
    .group(by="$category", count={"$sum": 1})\
    .sort("count", ascending=False)\
    .limit(10)\
    .project(category="$_id", count=1, _id=0)\
    .build()
```

### AtlasSearchBuilder

Build Atlas Search queries:

```python
from mongodb_query_builder import AtlasSearchBuilder, CompoundBuilder

# Text search with fuzzy matching
search = AtlasSearchBuilder()\
    .text("search term", path="title", fuzzy={"maxEdits": 2})\
    .build_stage()

# Compound search
compound = CompoundBuilder()
compound.must().text("required term", path="content")
compound.should().text("optional term", path="tags", score=2.0)
compound.filter().range("date", gte=datetime(2024, 1, 1))

search = AtlasSearchBuilder().compound(compound).build_stage()
```

## Requirements

- Python 3.8+
- pymongo (optional, for MongoDB operations)
- typing-extensions (for Python < 3.10)

## Documentation

### 📚 Getting Started
- [Installation & Quick Start](https://github.com/ch-dev401/mongodb-query-builder/blob/master/docs/markdown/getting-started.md)
- [Basic Queries Tutorial](https://github.com/ch-dev401/mongodb-query-builder/blob/master/docs/markdown/tutorials/01-basic-queries.md)

### 🔧 API Reference
- [QueryFilter API](https://github.com/ch-dev401/mongodb-query-builder/blob/master/docs/markdown/api/query-filter.md) - Query building methods
- [AggregateBuilder API](https://github.com/ch-dev401/mongodb-query-builder/blob/master/docs/markdown/api/aggregate-builder.md) - Aggregation pipeline methods
- [AtlasSearchBuilder API](https://github.com/ch-dev401/mongodb-query-builder/blob/master/docs/markdown/api/atlas-search-builder.md) - Atlas Search methods

### 📖 Guides
- [Migration Guide](https://github.com/ch-dev401/mongodb-query-builder/blob/master/docs/markdown/migration-guide.md) - Convert from raw MongoDB queries
- [Performance Guide](https://github.com/ch-dev401/mongodb-query-builder/blob/master/docs/markdown/performance-guide.md) - Optimization best practices

### 🛠️ Development
- [Contributing Guidelines](CONTRIBUTING.md)

### 📐 Full Documentation
- [Documentation Overview](https://github.com/ch-dev401/mongodb-query-builder/blob/master/docs/markdown/README.md) - Complete documentation index
- Online documentation available at: *(coming soon)*

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](https://github.com/ch-dev401/mongodb-query-builder/blob/master/docs/CONTRIBUTING.md) for guidelines.

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/ch-dev401/mongodb-query-builder/issues)
- Documentation: [Full documentation](https://github.com/ch-dev401/mongodb-query-builder)
