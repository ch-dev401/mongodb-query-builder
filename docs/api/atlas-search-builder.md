# AtlasSearchBuilder API Reference

The `AtlasSearchBuilder` class provides a fluent interface for building MongoDB Atlas Search queries.

## Class Overview

```python
from mongodb_query_builder import AtlasSearchBuilder
```

`AtlasSearchBuilder` allows you to construct Atlas Search queries with support for text search, compound queries, facets, and advanced search features.

## Constructor

```python
AtlasSearchBuilder(index: str = "default")
```

Creates a new AtlasSearchBuilder instance.

**Parameters:**
- `index` (str): The search index name (default: "default")

**Example:**
```python
search = AtlasSearchBuilder()
search_custom = AtlasSearchBuilder(index="custom_index")
```

## Core Methods

### build() -> Dict[str, Any]

Builds and returns the final search query dictionary.

**Returns:**
- Dict[str, Any]: The search query configuration

**Example:**
```python
search_query = AtlasSearchBuilder()
    .text("python developer", path="description")
    .build()
# Result: {"text": {"query": "python developer", "path": "description"}}
```

### build_stage() -> Dict[str, Any]

Builds and returns a complete $search aggregation stage.

**Returns:**
- Dict[str, Any]: The $search stage for aggregation pipeline

**Example:**
```python
search_stage = AtlasSearchBuilder()
    .text("mongodb", path="title")
    .build_stage()
# Result: {"$search": {"index": "default", "text": {"query": "mongodb", "path": "title"}}}
```

## Text Search Methods

### text(query: str, path: Union[str, List[str]], fuzzy: Optional[Dict[str, Any]] = None, score: Optional[Dict[str, Any]] = None) -> AtlasSearchBuilder

Performs text search on specified fields.

**Parameters:**
- `query` (str): The search query string
- `path` (Union[str, List[str]]): Field(s) to search
- `fuzzy` (Optional[Dict[str, Any]]): Fuzzy matching options
- `score` (Optional[Dict[str, Any]]): Scoring options

**Example:**
```python
# Simple text search
AtlasSearchBuilder().text("python", path="skills")

# Search multiple fields
AtlasSearchBuilder().text(
    "full stack developer",
    path=["title", "description", "requirements"]
)

# Fuzzy search
AtlasSearchBuilder().text(
    "pythn",  # Misspelled
    path="skills",
    fuzzy={"maxEdits": 2, "prefixLength": 2}
)

# Custom scoring
AtlasSearchBuilder().text(
    "senior",
    path="level",
    score={"boost": {"value": 2.0}}
)
```

### phrase(query: str, path: Union[str, List[str]], slop: Optional[int] = None, score: Optional[Dict[str, Any]] = None) -> AtlasSearchBuilder

Searches for exact phrase matches.

**Parameters:**
- `query` (str): The exact phrase to search
- `path` (Union[str, List[str]]): Field(s) to search
- `slop` (Optional[int]): Maximum word distance for matches
- `score` (Optional[Dict[str, Any]]): Scoring options

**Example:**
```python
# Exact phrase
AtlasSearchBuilder().phrase("machine learning", path="skills")

# Phrase with slop
AtlasSearchBuilder().phrase(
    "python developer",
    path="title",
    slop=2  # Allows up to 2 words between "python" and "developer"
)
```

### wildcard(query: str, path: Union[str, List[str]], allow_analyzed_field: bool = False) -> AtlasSearchBuilder

Performs wildcard pattern matching.

**Parameters:**
- `query` (str): Wildcard pattern (* for multiple chars, ? for single char)
- `path` (Union[str, List[str]]): Field(s) to search
- `allow_analyzed_field` (bool): Allow search on analyzed fields

**Example:**
```python
# Wildcard search
AtlasSearchBuilder().wildcard("py*", path="language")
AtlasSearchBuilder().wildcard("user?", path="username")
```

### regex(pattern: str, path: Union[str, List[str]], allow_analyzed_field: bool = False) -> AtlasSearchBuilder

Performs regular expression matching.

**Parameters:**
- `pattern` (str): Regular expression pattern
- `path` (Union[str, List[str]]): Field(s) to search
- `allow_analyzed_field` (bool): Allow search on analyzed fields

**Example:**
```python
# Regex search
AtlasSearchBuilder().regex(
    "^[A-Z]{2,4}-\\d{4}$",
    path="product_code"
)
```

### autocomplete(query: str, path: str, token_order: str = "any", fuzzy: Optional[Dict[str, Any]] = None) -> AtlasSearchBuilder

Provides autocomplete/type-ahead functionality.

**Parameters:**
- `query` (str): Partial query string
- `path` (str): Field configured for autocomplete
- `token_order` (str): "any" or "sequential"
- `fuzzy` (Optional[Dict[str, Any]]): Fuzzy matching options

**Example:**
```python
# Autocomplete search
AtlasSearchBuilder().autocomplete(
    "pyth",
    path="title",
    token_order="sequential"
)

# Fuzzy autocomplete
AtlasSearchBuilder().autocomplete(
    "mong",
    path="technology",
    fuzzy={"maxEdits": 1}
)
```

## Compound Queries

### compound(must: Optional[List[Dict[str, Any]]] = None, must_not: Optional[List[Dict[str, Any]]] = None, should: Optional[List[Dict[str, Any]]] = None, filter: Optional[List[Dict[str, Any]]] = None) -> AtlasSearchBuilder

Creates a compound query with multiple clauses.

**Parameters:**
- `must` (Optional[List[Dict[str, Any]]]): Required matches
- `must_not` (Optional[List[Dict[str, Any]]]): Excluded matches
- `should` (Optional[List[Dict[str, Any]]]): Optional matches (affects score)
- `filter` (Optional[List[Dict[str, Any]]]): Required matches (no score effect)

**Example:**
```python
from mongodb_query_builder import AtlasSearchBuilder, CompoundBuilder

# Using compound method directly
search = AtlasSearchBuilder().compound(
    must=[
        {"text": {"query": "python", "path": "skills"}}
    ],
    should=[
        {"text": {"query": "senior", "path": "level"}}
    ],
    filter=[
        {"range": {"path": "experience", "gte": 3}}
    ]
)

# Using CompoundBuilder (recommended)
compound = CompoundBuilder()
compound.must().text("python", path="skills")
compound.should().text("senior", path="level")
compound.filter().range("experience", gte=3)

search = AtlasSearchBuilder().compound(compound)
```

## CompoundBuilder Class

The `CompoundBuilder` class provides a fluent interface for building compound queries.

### Constructor

```python
CompoundBuilder()
```

### Methods

#### must() -> CompoundClauseBuilder

Returns a builder for required clauses.

```python
compound = CompoundBuilder()
compound.must().text("required term", path="field")
```

#### must_not() -> CompoundClauseBuilder

Returns a builder for excluded clauses.

```python
compound.must_not().text("excluded term", path="field")
```

#### should() -> CompoundClauseBuilder

Returns a builder for optional clauses that affect scoring.

```python
compound.should().text("bonus term", path="field", score=2.0)
```

#### filter() -> CompoundClauseBuilder

Returns a builder for required clauses that don't affect scoring.

```python
compound.filter().range("date", gte=datetime(2024, 1, 1))
```

### CompoundClauseBuilder Methods

All clause builders support the same search methods as AtlasSearchBuilder:

- `text(query, path, fuzzy=None, score=None)`
- `phrase(query, path, slop=None, score=None)`
- `wildcard(query, path, allow_analyzed_field=False)`
- `regex(pattern, path, allow_analyzed_field=False)`
- `range(path, gt=None, gte=None, lt=None, lte=None)`
- `equals(path, value)`
- `exists(path, value=True)`

## Range and Comparison Methods

### range(path: str, gt: Optional[Any] = None, gte: Optional[Any] = None, lt: Optional[Any] = None, lte: Optional[Any] = None) -> AtlasSearchBuilder

Searches for documents within a range.

**Parameters:**
- `path` (str): Field path
- `gt` (Optional[Any]): Greater than value
- `gte` (Optional[Any]): Greater than or equal value
- `lt` (Optional[Any]): Less than value
- `lte` (Optional[Any]): Less than or equal value

**Example:**
```python
# Numeric range
AtlasSearchBuilder().range("price", gte=100, lte=500)

# Date range
AtlasSearchBuilder().range(
    "created_date",
    gte=datetime(2024, 1, 1),
    lt=datetime(2024, 7, 1)
)
```

### equals(path: str, value: Any) -> AtlasSearchBuilder

Searches for exact value matches.

**Parameters:**
- `path` (str): Field path
- `value` (Any): Value to match

**Example:**
```python
AtlasSearchBuilder().equals("status", "active")
AtlasSearchBuilder().equals("category_id", 42)
```

### exists(path: str, value: bool = True) -> AtlasSearchBuilder

Searches for documents with or without a field.

**Parameters:**
- `path` (str): Field path
- `value` (bool): True to find documents with field, False for without

**Example:**
```python
AtlasSearchBuilder().exists("premium_features")
AtlasSearchBuilder().exists("deleted_at", value=False)
```

## Faceting

### facet(name: str, type: str, path: str, num_buckets: Optional[int] = None, boundaries: Optional[List[Union[int, float]]] = None) -> AtlasSearchBuilder

Adds faceted search for categorization and filtering.

**Parameters:**
- `name` (str): Facet name
- `type` (str): Facet type ("string", "number", "date")
- `path` (str): Field path
- `num_buckets` (Optional[int]): Number of buckets for numeric facets
- `boundaries` (Optional[List]): Custom boundaries for buckets

**Example:**
```python
# String facet
search = AtlasSearchBuilder()
    .text("laptop", path="name")
    .facet("brands", type="string", path="brand")
    .facet("categories", type="string", path="category")

# Numeric facet with auto buckets
search.facet("price_ranges", type="number", path="price", num_buckets=5)

# Numeric facet with custom boundaries
search.facet(
    "price_ranges",
    type="number",
    path="price",
    boundaries=[0, 100, 500, 1000, 5000]
)
```

## Search Options

### highlight(path: Union[str, List[str]], max_chars_to_examine: Optional[int] = None, max_num_passages: Optional[int] = None) -> AtlasSearchBuilder

Adds highlighting for matched terms.

**Parameters:**
- `path` (Union[str, List[str]]): Fields to highlight
- `max_chars_to_examine` (Optional[int]): Max characters to examine
- `max_num_passages` (Optional[int]): Max highlighted passages

**Example:**
```python
AtlasSearchBuilder()
    .text("python mongodb", path=["title", "description"])
    .highlight(
        path=["title", "description"],
        max_num_passages=3
    )
```

### count_documents(threshold: Optional[int] = None) -> AtlasSearchBuilder

Configures document counting behavior.

**Parameters:**
- `threshold` (Optional[int]): Counting threshold

**Example:**
```python
AtlasSearchBuilder()
    .text("query", path="field")
    .count_documents(threshold=1000)
```

### return_stored_source(value: bool = True) -> AtlasSearchBuilder

Controls whether to return stored source fields.

**Parameters:**
- `value` (bool): Whether to return stored source

**Example:**
```python
AtlasSearchBuilder()
    .text("query", path="field")
    .return_stored_source(True)
```

## Advanced Examples

### Complex E-commerce Search

```python
from mongodb_query_builder import AtlasSearchBuilder, CompoundBuilder

# Create compound query
compound = CompoundBuilder()

# Must have search term in name or description
compound.must().text(
    "wireless headphones",
    path=["name", "description"]
)

# Should prefer highly rated items
compound.should().range("rating", gte=4.0)

# Filter by price range
compound.filter().range("price", gte=50, lte=300)

# Filter by availability
compound.filter().equals("in_stock", True)

# Build search with facets
search = AtlasSearchBuilder()
    .compound(compound)
    .facet("brands", type="string", path="brand")
    .facet("price_ranges", type="number", path="price", 
           boundaries=[0, 50, 100, 200, 500, 1000])
    .facet("ratings", type="number", path="rating",
           boundaries=[0, 2, 3, 4, 4.5, 5])
    .highlight(["name", "description"])
    .build_stage()
```

### Multi-language Search

```python
# Search with language-specific analyzers
search = AtlasSearchBuilder(index="multilingual_index")
    .compound(
        should=[
            {"text": {"query": "ordinateur", "path": "title_fr"}},
            {"text": {"query": "computer", "path": "title_en"}},
            {"text": {"query": "コンピューター", "path": "title_ja"}}
        ]
    )
    .build_stage()
```

### Geo-aware Search

```python
# Search near a location
compound = CompoundBuilder()
compound.must().text("restaurant", path="type")
compound.filter().near(
    path="location",
    origin={"type": "Point", "coordinates": [-73.98, 40.75]},
    pivot=1000,  # 1km
    score={"boost": {"value": 2.0}}
)

search = AtlasSearchBuilder().compound(compound).build_stage()
```

### Search with Synonyms

```python
# Using synonym mapping
search = AtlasSearchBuilder(index="synonym_index")
    .text(
        "laptop",  # Will also match "notebook", "portable computer"
        path="product_name",
        synonyms="technology_synonyms"
    )
    .build_stage()
```

## Performance Tips

1. **Use Compound Queries**: Combine filters to reduce result sets early
2. **Index Configuration**: Ensure Atlas Search indexes are properly configured
3. **Field Selection**: Search only necessary fields
4. **Scoring Strategy**: Use `filter` clauses for non-scoring criteria
5. **Facet Optimization**: Limit facets to necessary fields

## Error Handling

AtlasSearchBuilder raises `AtlasSearchBuilderError` for invalid operations:

```python
from mongodb_query_builder import AtlasSearchBuilder, AtlasSearchBuilderError

try:
    search = AtlasSearchBuilder()
        .text("")  # Empty query
        .build()
except AtlasSearchBuilderError as e:
    print(f"Search construction error: {e}")
```

## Integration with Aggregation Pipeline

```python
from mongodb_query_builder import AggregateBuilder, AtlasSearchBuilder

# Create search stage
search_stage = AtlasSearchBuilder()
    .text("python developer", path=["title", "skills"])
    .build_stage()

# Use in aggregation pipeline
pipeline = AggregateBuilder()
    .add_stage(search_stage)
    .project(
        title=1,
        skills=1,
        score={"$meta": "searchScore"}
    )
    .sort("score", ascending=False)
    .limit(10)
    .build()
```

## See Also

- [QueryFilter](query-filter.md) - For standard MongoDB queries
- [AggregateBuilder](aggregate-builder.md) - For aggregation pipelines
- [Atlas Search Tutorial](../tutorials/03-atlas-search.md) - Step-by-step guide
- [MongoDB Atlas Search Docs](https://docs.atlas.mongodb.com/atlas-search/)
