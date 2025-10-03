# MongoDB Query Builder Documentation

Welcome to the MongoDB Query Builder documentation! This library provides a fluent, type-safe interface for constructing MongoDB queries, aggregation pipelines, and Atlas Search operations.

## 📚 Documentation Overview

### Getting Started
- [Installation & Quick Start](getting-started.md) - How to install and get started with MongoDB Query Builder
- Basic Concepts - Understanding QueryFilter, AggregateBuilder, and AtlasSearchBuilder

### Tutorials
Step-by-step guides for learning the library:

1. [Basic Queries](tutorials/01-basic-queries.md) - Simple queries and filters ✅
2. Aggregation Pipelines *(coming soon)* - Building complex data pipelines
3. Atlas Search *(coming soon)* - Full-text search with Atlas
4. Advanced Patterns *(coming soon)* - Complex query patterns and optimization

### API Reference
Detailed documentation for all components:

- [QueryFilter](api/query-filter.md) - Building MongoDB query filters ✅
- [AggregateBuilder](api/aggregate-builder.md) - Constructing aggregation pipelines ✅
- [AtlasSearchBuilder](api/atlas-search-builder.md) - Atlas Search queries ✅

### Guides
- [Migration Guide](migration-guide.md) - Converting raw MongoDB queries ✅
- [Performance Guide](performance-guide.md) - Query optimization tips ✅

### Cookbook *(coming soon)*
Real-world examples and patterns:

- User Authentication - User login and permission queries
- Product Catalog - E-commerce search and filtering
- Analytics Pipeline - Data aggregation for analytics
- Time Series - Working with time-series data

## 🚀 Quick Example

```python
from mongodb_query_builder import QueryFilter, AggregateBuilder

# Simple query
query = QueryFilter()
    .field("age").greater_than(18)
    .field("status").equals("active")
    .build()

# Aggregation pipeline
pipeline = AggregateBuilder()
    .match(QueryFilter().field("status").equals("active"))
    .group(by="$category", count={"$sum": 1})
    .sort("count", ascending=False)
    .limit(10)
    .build()
```

## 🔍 Finding What You Need

- **New to MongoDB Query Builder?** Start with the [Getting Started Guide](getting-started.md)
- **Looking for specific functionality?** Check the [API Reference](#api-reference)
- **Need examples?** Browse the [Cookbook](#cookbook) *(coming soon)*
- **Having issues?** Check our [GitHub Issues](https://github.com/ch-dev401/mongodb-query-builder/issues)

## 📖 Documentation Versions

This documentation is available in two formats:

1. **Markdown Documentation** (this version) - GitHub-friendly, easy to browse
2. **Sphinx Documentation** - Full API documentation with search functionality

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](../../CONTRIBUTING.md) for details on:
- Reporting issues
- Suggesting features
- Submitting pull requests
- Documentation improvements

## 📄 License

MongoDB Query Builder is released under the MIT License. See the [LICENSE](../../LICENSE) file for details.

---

**Need help?** 
- 📧 Open an issue on [GitHub](https://github.com/ch-dev401/mongodb-query-builder/issues)
- 💬 Join our [community discussions](https://github.com/ch-dev401/mongodb-query-builder/discussions)
- 📚 Read the [documentation](getting-started.md)
