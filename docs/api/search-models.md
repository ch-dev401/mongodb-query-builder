# Search Models API Reference

The Search Models module provides a declarative, class-based approach to defining MongoDB Atlas Search configurations. It offers type-safe field definitions and automatic validation for search operations.

## Overview

Search Models allow you to:
- Define search schemas using Python classes
- Specify field-level indexing and faceting configurations
- Build type-safe Atlas Search queries with automatic validation
- Support complex field names with dot notation
- Ensure consistency between your model and search operations

## IndexField

Field configuration class that defines how a field should be indexed and faceted.

### Constructor

```python
IndexField(
    string_index: bool = False,
    string_facet: bool = False,
    number_index: bool = False,
    number_facet: bool = False,
    date_index: bool = False,
    date_facet: bool = False
)
```

**Parameters:**
- `string_index`: Enable text/string search indexing
- `string_facet`: Enable string faceting for aggregations
- `number_index`: Enable numeric search indexing
- `number_facet`: Enable numeric faceting
- `date_index`: Enable date search indexing
- `date_facet`: Enable date faceting

### Properties

#### `is_searchable`
Returns `True` if the field is configured for search operations.

#### `is_facetable`
Returns `True` if the field supports faceting.

#### `search_type`
Returns the search type: `"string"`, `"number"`, `"date"`, or `None`.

#### `facet_type`
Returns the facet type: `"string"`, `"number"`, `"date"`, or `None`.

### Examples

```python
# Text search field
name_field = IndexField(string_index=True)

# Text search + faceting
category_field = IndexField(string_index=True, string_facet=True)

# Number faceting only
price_field = IndexField(number_facet=True)

# Date search + faceting
created_field = IndexField(date_index=True, date_facet=True)
```

## SearchModel

Base class for declarative search model definitions.

### Class Attributes

#### `index`
Name of the Atlas Search index (default: `"default"`).

#### `fields`
Optional dictionary for defining fields with complex names (e.g., dot notation).

### Defining Models

There are three ways to define search fields:

#### 1. Class Attributes (Simple Fields)

```python
class UserSearch(SearchModel):
    index = "users"
    
    name = IndexField(string_index=True)
    age = IndexField(number_index=True, number_facet=True)
    email = IndexField(string_index=True)
```

#### 2. Fields Dictionary (Complex Field Names)

```python
class MessageSearch(SearchModel):
    index = "messages"
    
    fields = {
        "type": IndexField(string_index=True, string_facet=True),
        "rawData.from": IndexField(string_index=True),
        "rawData.to": IndexField(string_index=True),
        "metadata.timestamp": IndexField(date_index=True),
    }
```

#### 3. Combined Approach

```python
class ProductSearch(SearchModel):
    index = "products"
    
    # Simple fields
    name = IndexField(string_index=True)
    description = IndexField(string_index=True)
    
    # Complex fields
    fields = {
        "price.amount": IndexField(number_index=True, number_facet=True),
        "metadata.brand": IndexField(string_facet=True),
    }
```

### Class Methods

#### `get_field(field_name: str) -> Optional[IndexField]`
Retrieve field configuration by name.

```python
field = UserSearch.get_field("name")
if field and field.is_searchable:
    # Field is searchable
    pass
```

#### `get_searchable_fields() -> Dict[str, IndexField]`
Get all fields configured for searching.

```python
searchable = UserSearch.get_searchable_fields()
# Returns: {"name": IndexField(...), "email": IndexField(...)}
```

#### `get_facetable_fields() -> Dict[str, IndexField]`
Get all fields configured for faceting.

```python
facetable = ProductSearch.get_facetable_fields()
# Returns: {"category": IndexField(...), "price.amount": IndexField(...)}
```

#### `validate_field(field_name: str, operation: str) -> None`
Validate that a field supports a specific operation.

```python
try:
    UserSearch.validate_field("name", "search")  # OK
    UserSearch.validate_field("name", "facet")   # Raises ValueError
except ValueError as e:
    print(e)
```

#### `get_all_fields() -> Dict[str, IndexField]`
Get all defined fields.

```python
all_fields = UserSearch.get_all_fields()
```

#### `builder() -> AtlasSearchBuilder`
Get a raw AtlasSearchBuilder for advanced use cases.

```python
builder = UserSearch.builder()
builder.text("query", path="name")
```

#### `search() -> SearchQuery`
Start building a search query (recommended approach).

```python
query = UserSearch.search()
query.text("john", field="name")
```

## SearchQuery

Type-safe query builder that integrates with SearchModel.

### Methods

#### `text(query: str, field: str, fuzzy: Optional[Dict] = None, score: Optional[float] = None)`
Add text search for a field.

```python
UserSearch.search().text("john", field="name")

# With fuzzy matching
UserSearch.search().text(
    "john",
    field="name",
    fuzzy={"maxEdits": 2}
)

# With score boost
UserSearch.search().text(
    "john",
    field="name",
    score=2.0
)
```

**Raises:**
- `ValueError`: If field isn't configured for text search

#### `phrase(query: str, field: str, slop: int = 0, score: Optional[float] = None)`
Add phrase search for a field.

```python
UserSearch.search().phrase(
    "software engineer",
    field="bio",
    slop=2
)
```

#### `autocomplete(query: str, field: str, fuzzy: Optional[Dict] = None)`
Add autocomplete search.

```python
UserSearch.search().autocomplete("joh", field="username")
```

#### `compound(compound_builder: CompoundBuilder)`
Use a compound query builder.

```python
compound = CompoundBuilder()
compound.must().text("python", path="skills")
compound.should().text("senior", path="level")

UserSearch.search().compound(compound)
```

#### `facet(field: str, num_buckets: int = 10, boundaries: Optional[List] = None)`
Add facet for a field.

```python
# String facet
UserSearch.search().facet("category")

# Number facet with boundaries
ProductSearch.search().facet(
    "price.amount",
    boundaries=[0, 50, 100, 200, 500]
)
```

**Raises:**
- `ValueError`: If field isn't configured for faceting

#### `facet_all(**kwargs)`
Add facets for all facetable fields.

```python
UserSearch.search().facet_all()
```

#### `use_facet_operator(operator: Union[CompoundBuilder, Dict, None] = None)`
Enable facet operator mode for complex faceted searches.

```python
compound = CompoundBuilder()
compound.must().equals("userId", user_id)

MessageSearch.search()
    .use_facet_operator(compound)
    .facet("type")
    .facet("status")
```

#### `count(type: str = "lowerBound", threshold: Optional[int] = None)`
Configure count options.

```python
UserSearch.search()
    .text("query", field="name")
    .count(type="total", threshold=1000)
```

#### `raw_builder() -> AtlasSearchBuilder`
Access the underlying AtlasSearchBuilder.

```python
builder = UserSearch.search().raw_builder()
```

#### `build() -> Dict[str, Any]`
Build the search query dictionary.

```python
query_dict = UserSearch.search()
    .text("john", field="name")
    .build()
```

#### `build_stage() -> Dict[str, Any]`
Build as `$search` aggregation pipeline stage.

```python
stage = UserSearch.search()
    .text("john", field="name")
    .build_stage()

# Use in aggregation
pipeline = [stage, {"$limit": 10}]
```

#### `build_meta_stage() -> Dict[str, Any]`
Build as `$searchMeta` stage (for counting/faceting without documents).

```python
meta_stage = UserSearch.search()
    .facet_all()
    .build_meta_stage()
```

## Complete Examples

### Basic Search Model

```python
from mongodb_query_builder import SearchModel, IndexField

class UserSearch(SearchModel):
    index = "users"
    
    username = IndexField(string_index=True)
    email = IndexField(string_index=True)
    age = IndexField(number_index=True, number_facet=True)
    role = IndexField(string_facet=True)
    department = IndexField(string_facet=True)

# Simple text search
results = UserSearch.search()
    .text("john", field="username")
    .build()

# Search with facets
results = UserSearch.search()
    .text("engineer", field="role")
    .facet("department")
    .facet("age", boundaries=[18, 30, 40, 50, 60])
    .build()

# Autocomplete
results = UserSearch.search()
    .autocomplete("joh", field="username")
    .build()
```

### Complex Field Names

```python
class MessageSearch(SearchModel):
    index = "messages"
    
    fields = {
        "type": IndexField(string_index=True, string_facet=True),
        "rawData.from": IndexField(string_index=True, string_facet=True),
        "rawData.to": IndexField(string_index=True),
        "rawData.subject": IndexField(string_index=True),
        "metadata.timestamp": IndexField(date_index=True, date_facet=True),
        "status": IndexField(string_index=True, string_facet=True),
    }

# Search nested fields
results = MessageSearch.search()
    .text("important", field="rawData.subject")
    .facet("type")
    .facet("status")
    .build()

# Search with sender faceting
results = MessageSearch.search()
    .text("update", field="rawData.subject")
    .facet("rawData.from")
    .build()
```

### Product Catalog Search

```python
class ProductSearch(SearchModel):
    index = "products"
    
    # Simple fields
    name = IndexField(string_index=True)
    description = IndexField(string_index=True)
    category = IndexField(string_index=True, string_facet=True)
    
    # Complex nested fields
    fields = {
        "price.amount": IndexField(number_index=True, number_facet=True),
        "price.currency": IndexField(string_facet=True),
        "metadata.brand": IndexField(string_index=True, string_facet=True),
        "metadata.tags": IndexField(string_index=True),
        "inventory.inStock": IndexField(number_index=True),
    }

# Complex search with multiple facets
compound = CompoundBuilder()
compound.must().text("laptop", path="name")
compound.filter().text("electronics", path="category")
compound.filter().range("price.amount", gte=500, lte=2000)

results = ProductSearch.search()
    .compound(compound)
    .facet("category")
    .facet("metadata.brand")
    .facet("price.amount", boundaries=[0, 500, 1000, 2000, 5000])
    .count(type="total")
    .build()
```

### Facet Operator Pattern

```python
from bson import ObjectId

class MessageSearch(SearchModel):
    index = "messages"
    
    fields = {
        "type": IndexField(string_index=True, string_facet=True),
        "userId": IndexField(string_index=True),
        "status": IndexField(string_index=True, string_facet=True),
    }

# Get facets for a specific user
user_id = ObjectId("507f1f77bcf86cd799439011")

compound = CompoundBuilder()
compound.must().equals("userId", user_id)

# Use facet operator to filter before faceting
meta_stage = MessageSearch.search()
    .use_facet_operator(compound)
    .facet("type")
    .facet("status")
    .build_meta_stage()

# This can be used in an aggregation pipeline
# to get facet counts for a specific user's messages
```

## Best Practices

### 1. Index Configuration

Match your IndexField definitions to your actual Atlas Search index:

```python
# Your Atlas Search index should match this configuration
class UserSearch(SearchModel):
    index = "users_index"  # Name in Atlas
    
    # If searchable, configure in Atlas as "string" type
    name = IndexField(string_index=True)
    
    # If facetable, configure in Atlas with facet: true
    department = IndexField(string_facet=True)
```

### 2. Validation

Always validate field operations:

```python
# The SearchQuery methods automatically validate
try:
    # This will raise ValueError if 'name' isn't facetable
    UserSearch.search().facet("name")
except ValueError as e:
    print(f"Invalid operation: {e}")
```

### 3. Compound Queries

Use compound queries for complex search logic:

```python
compound = CompoundBuilder()
compound.must().text("python", path="skills")      # Required
compound.should().text("senior", path="level")      # Boosts score
compound.filter().range("experience", gte=3)        # Filters without scoring

UserSearch.search()
    .compound(compound)
    .facet_all()
    .build()
```

### 4. Autocomplete

Configure autocomplete fields properly:

```python
class UserSearch(SearchModel):
    # Use string_index for autocomplete
    username = IndexField(string_index=True)

# Atlas index should have autocomplete type for this field
results = UserSearch.search()
    .autocomplete("joh", field="username", fuzzy={"maxEdits": 1})
    .build()
```

## See Also

- [Atlas Search Builder API](atlas-search-builder.md)
- [Aggregate Builder API](aggregate-builder.md)
- [Atlas Search Tutorials](../tutorials/03-atlas-search.md)
