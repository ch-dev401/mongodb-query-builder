# MongoDB Query Builder

A Python library for building MongoDB queries with a clean, intuitive API.

[![PyPI version](https://badge.fury.io/py/mongodb-query-builder.svg)](https://badge.fury.io/py/mongodb-query-builder)
[![Python versions](https://img.shields.io/pypi/pyversions/mongodb-query-builder.svg)](https://pypi.org/project/mongodb-query-builder/)
[![License](https://img.shields.io/pypi/l/mongodb-query-builder.svg)](https://github.com/yourusername/mongodb-builder/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/mongodb-query-builder/badge/?version=latest)](https://mongodb-query-builder.readthedocs.io/en/latest/?badge=latest)

## Overview

MongoDB Query Builder provides a type-safe, intuitive way to build complex MongoDB queries in Python. It supports:

- ✅ **Type-safe query construction** - Full typing support with IDE autocomplete
- ✅ **Chainable API** - Build complex queries with method chaining
- ✅ **Aggregation pipelines** - Simplified aggregation pipeline construction
- ✅ **Atlas Search integration** - Native support for MongoDB Atlas Search
- ✅ **Comprehensive operators** - Support for all MongoDB query operators
- ✅ **Python 3.8+** - Modern Python support

## Quick Example

```python
from mongodb_query_builder import QueryFilter, AggregateBuilder

# Simple query
query = QueryFilter().where("age").gte(18).where("status").eq("active")

# Complex aggregation
pipeline = (
    AggregateBuilder()
    .match({"category": "electronics"})
    .group({
        "_id": "$brand",
        "total_sales": {"$sum": "$price"},
        "avg_rating": {"$avg": "$rating"}
    })
    .sort("-total_sales")
    .limit(10)
    .build()
)
```

## Features

### 🔍 Intuitive Query Building

Build queries using a natural, chainable syntax:

```python
query = (
    QueryFilter()
    .where("price").between(100, 500)
    .where("category").in_(["electronics", "computers"])
    .where("rating").gte(4.0)
)
```

### 🚀 Powerful Aggregation Pipelines

Create complex aggregation pipelines with ease:

```python
pipeline = (
    AggregateBuilder()
    .match({"status": "shipped"})
    .lookup("customers", "customer_id", "_id", "customer_details")
    .unwind("$customer_details")
    .group({
        "_id": "$customer_details.country",
        "total_orders": {"$sum": 1},
        "revenue": {"$sum": "$total_amount"}
    })
    .build()
)
```

### 🔎 Atlas Search Integration

Native support for MongoDB Atlas Search:

```python
from mongodb_query_builder import AtlasSearchBuilder

search = (
    AtlasSearchBuilder()
    .text("laptop", path="title")
    .range("price", gte=500, lte=2000)
    .facet("category", "brand")
    .highlight("description")
    .build()
)
```

## Installation

Install using pip:

```bash
pip install mongodb-query-builder
```

Or with motor (async support):

```bash
pip install mongodb-query-builder[motor]
```

## Documentation

- [Getting Started](getting-started.md) - Installation and basic usage
- [User Guide](tutorials/01-basic-queries.md) - Comprehensive tutorials
- [API Reference](api/query-filter.md) - Complete API documentation
- [Cookbook](cookbook/index.md) - Real-world examples and patterns

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/yourusername/mongodb-builder/blob/main/CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/yourusername/mongodb-builder/blob/main/LICENSE) file for details.
