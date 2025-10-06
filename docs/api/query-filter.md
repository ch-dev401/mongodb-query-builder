# QueryFilter API Reference

The `QueryFilter` class provides a fluent interface for building MongoDB query filters.

## Class Overview

```python
from mongodb_query_builder import QueryFilter
```

`QueryFilter` allows you to construct MongoDB queries using a chainable API that provides type safety and validation.

## Constructor

```python
QueryFilter()
```

Creates a new QueryFilter instance with an empty query.

**Example:**
```python
query = QueryFilter()
```

## Core Methods

### field(name: str) -> QueryFilter

Sets the current field for subsequent operations.

**Parameters:**
- `name` (str): The field name to query

**Returns:**
- QueryFilter: Returns self for method chaining

**Example:**
```python
query = QueryFilter().field("age").greater_than(18)
```

### build() -> Dict[str, Any]

Builds and returns the final MongoDB query dictionary.

**Returns:**
- Dict[str, Any]: The MongoDB query document

**Example:**
```python
query_dict = QueryFilter().field("status").equals("active").build()
# Result: {"status": "active"}
```

## Comparison Operators

### equals(value: Any) -> QueryFilter

Matches documents where the field equals the specified value.

**Parameters:**
- `value` (Any): The value to match

**Example:**
```python
QueryFilter().field("status").equals("active")
# Result: {"status": "active"}
```

### not_equals(value: Any) -> QueryFilter

Matches documents where the field does not equal the specified value.

**Parameters:**
- `value` (Any): The value to not match

**Example:**
```python
QueryFilter().field("status").not_equals("deleted")
# Result: {"status": {"$ne": "deleted"}}
```

### greater_than(value: Union[int, float, datetime]) -> QueryFilter

Matches documents where the field is greater than the specified value.

**Parameters:**
- `value` (Union[int, float, datetime]): The value to compare against

**Example:**
```python
QueryFilter().field("age").greater_than(18)
# Result: {"age": {"$gt": 18}}
```

### greater_than_or_equal(value: Union[int, float, datetime]) -> QueryFilter

Matches documents where the field is greater than or equal to the specified value.

**Parameters:**
- `value` (Union[int, float, datetime]): The value to compare against

**Example:**
```python
QueryFilter().field("age").greater_than_or_equal(18)
# Result: {"age": {"$gte": 18}}
```

### less_than(value: Union[int, float, datetime]) -> QueryFilter

Matches documents where the field is less than the specified value.

**Parameters:**
- `value` (Union[int, float, datetime]): The value to compare against

**Example:**
```python
QueryFilter().field("price").less_than(100)
# Result: {"price": {"$lt": 100}}
```

### less_than_or_equal(value: Union[int, float, datetime]) -> QueryFilter

Matches documents where the field is less than or equal to the specified value.

**Parameters:**
- `value` (Union[int, float, datetime]): The value to compare against

**Example:**
```python
QueryFilter().field("price").less_than_or_equal(100)
# Result: {"price": {"$lte": 100}}
```

### between(start: Union[int, float, datetime], end: Union[int, float, datetime]) -> QueryFilter

Matches documents where the field value is between start and end (inclusive).

**Parameters:**
- `start` (Union[int, float, datetime]): The minimum value (inclusive)
- `end` (Union[int, float, datetime]): The maximum value (inclusive)

**Example:**
```python
QueryFilter().field("age").between(18, 65)
# Result: {"age": {"$gte": 18, "$lte": 65}}
```

### in_(values: List[Any]) -> QueryFilter

Matches documents where the field value is in the specified list.

**Parameters:**
- `values` (List[Any]): List of values to match

**Example:**
```python
QueryFilter().field("status").in_(["active", "pending"])
# Result: {"status": {"$in": ["active", "pending"]}}
```

### not_in(values: List[Any]) -> QueryFilter

Matches documents where the field value is not in the specified list.

**Parameters:**
- `values` (List[Any]): List of values to not match

**Example:**
```python
QueryFilter().field("status").not_in(["deleted", "archived"])
# Result: {"status": {"$nin": ["deleted", "archived"]}}
```

## Logical Operators

### all_of(conditions: List[QueryFilter]) -> QueryFilter

Combines multiple conditions with AND logic.

**Parameters:**
- `conditions` (List[QueryFilter]): List of QueryFilter conditions

**Example:**
```python
QueryFilter().all_of([
    QueryFilter().field("age").greater_than(18),
    QueryFilter().field("status").equals("active")
])
# Result: {"$and": [{"age": {"$gt": 18}}, {"status": "active"}]}
```

### any_of(conditions: List[QueryFilter]) -> QueryFilter

Combines multiple conditions with OR logic.

**Parameters:**
- `conditions` (List[QueryFilter]): List of QueryFilter conditions

**Example:**
```python
QueryFilter().any_of([
    QueryFilter().field("role").equals("admin"),
    QueryFilter().field("role").equals("moderator")
])
# Result: {"$or": [{"role": "admin"}, {"role": "moderator"}]}
```

### none_of(conditions: List[QueryFilter]) -> QueryFilter

Combines multiple conditions with NOR logic.

**Parameters:**
- `conditions` (List[QueryFilter]): List of QueryFilter conditions

**Example:**
```python
QueryFilter().none_of([
    QueryFilter().field("status").equals("deleted"),
    QueryFilter().field("status").equals("archived")
])
# Result: {"$nor": [{"status": "deleted"}, {"status": "archived"}]}
```

### not_(condition: QueryFilter) -> QueryFilter

Negates a condition.

**Parameters:**
- `condition` (QueryFilter): The condition to negate

**Example:**
```python
QueryFilter().not_(
    QueryFilter().field("status").equals("active")
)
# Result: {"$not": {"status": "active"}}
```

## Array Operators

### array_contains(value: Any) -> QueryFilter

Matches arrays that contain the specified value.

**Parameters:**
- `value` (Any): The value to check for

**Example:**
```python
QueryFilter().field("tags").array_contains("python")
# Result: {"tags": "python"}
```

### array_contains_all(values: List[Any]) -> QueryFilter

Matches arrays that contain all specified values.

**Parameters:**
- `values` (List[Any]): List of values that must all be present

**Example:**
```python
QueryFilter().field("skills").array_contains_all(["python", "mongodb"])
# Result: {"skills": {"$all": ["python", "mongodb"]}}
```

### array_size(size: int) -> QueryFilter

Matches arrays with the specified size.

**Parameters:**
- `size` (int): The exact array size

**Example:**
```python
QueryFilter().field("items").array_size(3)
# Result: {"items": {"$size": 3}}
```

### array_element_match(condition: Dict[str, Any]) -> QueryFilter

Matches arrays where at least one element matches the condition.

**Parameters:**
- `condition` (Dict[str, Any]): The condition for array elements

**Example:**
```python
QueryFilter().field("scores").array_element_match({"$gt": 80})
# Result: {"scores": {"$elemMatch": {"$gt": 80}}}
```

## String Operators

### starts_with(prefix: str, case_sensitive: bool = True) -> QueryFilter

Matches strings that start with the specified prefix.

**Parameters:**
- `prefix` (str): The prefix to match
- `case_sensitive` (bool): Whether the match is case-sensitive (default: True)

**Example:**
```python
QueryFilter().field("name").starts_with("John")
# Result: {"name": {"$regex": "^John"}}

QueryFilter().field("name").starts_with("john", case_sensitive=False)
# Result: {"name": {"$regex": "^john", "$options": "i"}}
```

### ends_with(suffix: str, case_sensitive: bool = True) -> QueryFilter

Matches strings that end with the specified suffix.

**Parameters:**
- `suffix` (str): The suffix to match
- `case_sensitive` (bool): Whether the match is case-sensitive (default: True)

**Example:**
```python
QueryFilter().field("email").ends_with("@example.com")
# Result: {"email": {"$regex": "@example\\.com$"}}
```

### contains(substring: str, case_sensitive: bool = True) -> QueryFilter

Matches strings that contain the specified substring.

**Parameters:**
- `substring` (str): The substring to match
- `case_sensitive` (bool): Whether the match is case-sensitive (default: True)

**Example:**
```python
QueryFilter().field("description").contains("python")
# Result: {"description": {"$regex": "python"}}
```

### regex(pattern: str, options: Optional[str] = None) -> QueryFilter

Matches strings using a regular expression.

**Parameters:**
- `pattern` (str): The regular expression pattern
- `options` (Optional[str]): MongoDB regex options (e.g., "i" for case-insensitive)

**Example:**
```python
QueryFilter().field("email").regex(r".*@example\.com$", "i")
# Result: {"email": {"$regex": ".*@example\\.com$", "$options": "i"}}
```

## Element Operators

### exists(value: bool = True) -> QueryFilter

Matches documents that have (or don't have) the specified field.

**Parameters:**
- `value` (bool): True to match documents with the field, False for without

**Example:**
```python
QueryFilter().field("email").exists()
# Result: {"email": {"$exists": true}}

QueryFilter().field("deleted_at").exists(False)
# Result: {"deleted_at": {"$exists": false}}
```

### type_check(bson_type: Union[str, int]) -> QueryFilter

Matches documents where the field is of the specified BSON type.

**Parameters:**
- `bson_type` (Union[str, int]): The BSON type name or number

**Example:**
```python
QueryFilter().field("age").type_check("int")
# Result: {"age": {"$type": "int"}}

QueryFilter().field("tags").type_check("array")
# Result: {"tags": {"$type": "array"}}
```

## Geo Operators

### near(coordinates: List[float], max_distance: Optional[float] = None, min_distance: Optional[float] = None) -> QueryFilter

Finds documents near a geographic point.

**Parameters:**
- `coordinates` (List[float]): [longitude, latitude] coordinates
- `max_distance` (Optional[float]): Maximum distance in meters
- `min_distance` (Optional[float]): Minimum distance in meters

**Example:**
```python
QueryFilter().field("location").near([40.7128, -74.0060], max_distance=1000)
# Result: {"location": {"$near": {"$geometry": {"type": "Point", "coordinates": [40.7128, -74.0060]}, "$maxDistance": 1000}}}
```

### within_box(bottom_left: List[float], top_right: List[float]) -> QueryFilter

Finds documents within a rectangular area.

**Parameters:**
- `bottom_left` (List[float]): [longitude, latitude] of bottom-left corner
- `top_right` (List[float]): [longitude, latitude] of top-right corner

**Example:**
```python
QueryFilter().field("location").within_box([40.0, -75.0], [41.0, -73.0])
# Result: {"location": {"$geoWithin": {"$box": [[40.0, -75.0], [41.0, -73.0]]}}}
```

## Advanced Usage

### Combining Multiple Fields

```python
query = QueryFilter()
    .field("age").greater_than(18)
    .field("status").equals("active")
    .field("role").in_(["user", "admin"])
    .build()
# Result: {"age": {"$gt": 18}, "status": "active", "role": {"$in": ["user", "admin"]}}
```

### Nested Field Queries

```python
query = QueryFilter()
    .field("address.city").equals("New York")
    .field("address.zipcode").starts_with("100")
    .build()
# Result: {"address.city": "New York", "address.zipcode": {"$regex": "^100"}}
```

### Complex Logical Combinations

```python
query = QueryFilter().all_of([
    QueryFilter().field("type").equals("product"),
    QueryFilter().any_of([
        QueryFilter().field("price").less_than(50),
        QueryFilter().all_of([
            QueryFilter().field("price").between(50, 100),
            QueryFilter().field("discount").greater_than(0.2)
        ])
    ])
]).build()
```

## Error Handling

QueryFilter raises `QueryFilterError` for invalid operations:

```python
from mongodb_query_builder import QueryFilter, QueryFilterError

try:
    # This will raise an error - no field specified
    query = QueryFilter().equals("value").build()
except QueryFilterError as e:
    print(f"Error: {e}")
```

Common error scenarios:
- Using operators without calling `field()` first
- Passing invalid types to operators
- Empty arrays for `in_()` or `array_contains_all()`
- Invalid regex patterns

## Performance Tips

1. **Use indexes**: Design queries to take advantage of MongoDB indexes
2. **Limit fields**: Query only the fields you need
3. **Use type-appropriate operators**: Use numeric operators for numbers, string operators for strings
4. **Avoid complex regex**: Anchored regex (^prefix) performs better than contains patterns
5. **Combine conditions efficiently**: Use compound indexes for multi-field queries

## See Also

- [AggregateBuilder](aggregate-builder.md) - For aggregation pipelines
- [AtlasSearchBuilder](atlas-search-builder.md) - For Atlas Search queries
- [Migration Guide](../migration-guide.md) - Converting from raw MongoDB queries
- [Performance Guide](../performance-guide.md) - Query optimization tips
