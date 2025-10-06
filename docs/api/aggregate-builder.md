# AggregateBuilder API Reference

The `AggregateBuilder` class provides a fluent interface for building MongoDB aggregation pipelines.

## Class Overview

```python
from mongodb_query_builder import AggregateBuilder
```

`AggregateBuilder` allows you to construct MongoDB aggregation pipelines using a chainable API that provides type safety and intuitive method names.

## Constructor

```python
AggregateBuilder()
```

Creates a new AggregateBuilder instance with an empty pipeline.

**Example:**
```python
pipeline_builder = AggregateBuilder()
```

## Core Methods

### build() -> List[Dict[str, Any]]

Builds and returns the final aggregation pipeline as a list of stages.

**Returns:**
- List[Dict[str, Any]]: The MongoDB aggregation pipeline

**Example:**
```python
pipeline = AggregateBuilder()
    .match(QueryFilter().field("status").equals("active"))
    .limit(10)
    .build()
# Result: [{"$match": {"status": "active"}}, {"$limit": 10}]
```

## Pipeline Stages

### match(filter_query: Union[QueryFilter, Dict[str, Any]]) -> AggregateBuilder

Filters documents using a query filter.

**Parameters:**
- `filter_query` (Union[QueryFilter, Dict[str, Any]]): Query filter or dictionary

**Example:**
```python
# Using QueryFilter
AggregateBuilder().match(
    QueryFilter().field("age").greater_than(18)
)

# Using dictionary
AggregateBuilder().match({"age": {"$gt": 18}})
```

### project(**fields: Union[int, str, Dict[str, Any]]) -> AggregateBuilder

Reshapes documents by including, excluding, or computing new fields.

**Parameters:**
- `**fields`: Field specifications (1 to include, 0 to exclude, or expressions)

**Example:**
```python
# Include/exclude fields
AggregateBuilder().project(
    name=1,
    email=1,
    _id=0
)

# Computed fields
AggregateBuilder().project(
    fullName={"$concat": ["$firstName", " ", "$lastName"]},
    age={"$subtract": [{"$year": "$$NOW"}, {"$year": "$birthDate"}]}
)
```

### group(by: Optional[Union[str, Dict[str, Any]]] = None, **accumulators: Dict[str, Any]) -> AggregateBuilder

Groups documents and applies accumulator expressions.

**Parameters:**
- `by` (Optional[Union[str, Dict[str, Any]]]): Grouping expression or field
- `**accumulators`: Accumulator expressions

**Example:**
```python
# Group by field
AggregateBuilder().group(
    by="$category",
    count={"$sum": 1},
    avgPrice={"$avg": "$price"}
)

# Group by multiple fields
AggregateBuilder().group(
    by={"category": "$category", "status": "$status"},
    total={"$sum": "$amount"}
)

# Group all documents
AggregateBuilder().group(
    by=None,
    totalRevenue={"$sum": "$revenue"}
)
```

### sort(field: Optional[str] = None, ascending: bool = True, **fields: int) -> AggregateBuilder

Sorts documents by one or more fields.

**Parameters:**
- `field` (Optional[str]): Single field to sort by
- `ascending` (bool): Sort direction for single field (default: True)
- `**fields`: Multiple fields with sort direction (1 for ascending, -1 for descending)

**Example:**
```python
# Single field sort
AggregateBuilder().sort("age", ascending=False)

# Multiple field sort
AggregateBuilder().sort(age=-1, name=1)
```

### limit(count: int) -> AggregateBuilder

Limits the number of documents in the pipeline.

**Parameters:**
- `count` (int): Maximum number of documents

**Example:**
```python
AggregateBuilder().limit(10)
```

### skip(count: int) -> AggregateBuilder

Skips a specified number of documents.

**Parameters:**
- `count` (int): Number of documents to skip

**Example:**
```python
AggregateBuilder().skip(20).limit(10)  # Pagination
```

### unwind(path: str, preserve_null_and_empty_arrays: bool = False, include_array_index: Optional[str] = None) -> AggregateBuilder

Deconstructs an array field into multiple documents.

**Parameters:**
- `path` (str): Array field path (with or without $)
- `preserve_null_and_empty_arrays` (bool): Keep documents without the array field
- `include_array_index` (Optional[str]): Field name for array index

**Example:**
```python
# Simple unwind
AggregateBuilder().unwind("$tags")

# Preserve empty arrays
AggregateBuilder().unwind(
    "$items",
    preserve_null_and_empty_arrays=True
)

# Include array index
AggregateBuilder().unwind(
    "$products",
    include_array_index="productIndex"
)
```

### lookup(from_collection: str, local_field: str, foreign_field: str, as_field: str) -> AggregateBuilder

Performs a left outer join with another collection.

**Parameters:**
- `from_collection` (str): The collection to join
- `local_field` (str): Field from input documents
- `foreign_field` (str): Field from joined collection
- `as_field` (str): Output array field name

**Example:**
```python
AggregateBuilder().lookup(
    from_collection="users",
    local_field="userId",
    foreign_field="_id",
    as_field="userDetails"
)
```

### add_fields(**fields: Dict[str, Any]) -> AggregateBuilder

Adds new fields to documents.

**Parameters:**
- `**fields`: Field expressions to add

**Example:**
```python
AggregateBuilder().add_fields(
    total={"$multiply": ["$price", "$quantity"]},
    discountedPrice={"$multiply": ["$price", 0.9]}
)
```

### set(**fields: Dict[str, Any]) -> AggregateBuilder

Alias for add_fields (MongoDB 4.2+).

**Parameters:**
- `**fields`: Field expressions to set

**Example:**
```python
AggregateBuilder().set(
    status="processed",
    processedAt="$$NOW"
)
```

### unset(fields: Union[str, List[str]]) -> AggregateBuilder

Removes fields from documents.

**Parameters:**
- `fields` (Union[str, List[str]]): Field(s) to remove

**Example:**
```python
# Remove single field
AggregateBuilder().unset("tempField")

# Remove multiple fields
AggregateBuilder().unset(["temp1", "temp2", "internal"])
```

### replace_root(new_root: Union[str, Dict[str, Any]]) -> AggregateBuilder

Replaces the document with a new root document.

**Parameters:**
- `new_root` (Union[str, Dict[str, Any]]): New root document or field path

**Example:**
```python
# Replace with embedded document
AggregateBuilder().replace_root("$details")

# Replace with computed document
AggregateBuilder().replace_root({
    "user": "$name",
    "totalSpent": {"$sum": "$orders.amount"}
})
```

### count(field_name: str = "count") -> AggregateBuilder

Counts the number of documents and stores in a field.

**Parameters:**
- `field_name` (str): Output field name (default: "count")

**Example:**
```python
AggregateBuilder()
    .match(QueryFilter().field("status").equals("active"))
    .count("activeUsers")
```

### facet(**facets: Dict[str, List[Dict[str, Any]]]) -> AggregateBuilder

Processes multiple aggregation pipelines in a single stage.

**Parameters:**
- `**facets`: Named sub-pipelines

**Example:**
```python
AggregateBuilder().facet(
    categoryCounts=[
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ],
    priceRanges=[
        {"$bucket": {
            "groupBy": "$price",
            "boundaries": [0, 50, 100, 200],
            "default": "Other"
        }}
    ],
    topProducts=[
        {"$sort": {"sales": -1}},
        {"$limit": 5}
    ]
)
```

### bucket(group_by: str, boundaries: List[Union[int, float]], default: Optional[str] = None, output: Optional[Dict[str, Any]] = None) -> AggregateBuilder

Groups documents into buckets.

**Parameters:**
- `group_by` (str): Expression to group by
- `boundaries` (List[Union[int, float]]): Bucket boundaries
- `default` (Optional[str]): Bucket for out-of-range values
- `output` (Optional[Dict[str, Any]]): Output specifications

**Example:**
```python
AggregateBuilder().bucket(
    group_by="$age",
    boundaries=[0, 18, 30, 50, 65, 100],
    default="Other",
    output={
        "count": {"$sum": 1},
        "users": {"$push": "$name"}
    }
)
```

### bucket_auto(group_by: str, buckets: int, output: Optional[Dict[str, Any]] = None) -> AggregateBuilder

Automatically creates evenly distributed buckets.

**Parameters:**
- `group_by` (str): Expression to group by
- `buckets` (int): Number of buckets
- `output` (Optional[Dict[str, Any]]): Output specifications

**Example:**
```python
AggregateBuilder().bucket_auto(
    group_by="$price",
    buckets=5,
    output={
        "count": {"$sum": 1},
        "avgPrice": {"$avg": "$price"}
    }
)
```

### sample(size: int) -> AggregateBuilder

Randomly selects documents.

**Parameters:**
- `size` (int): Number of documents to sample

**Example:**
```python
AggregateBuilder().sample(100)
```

### out(collection: str) -> AggregateBuilder

Writes pipeline results to a collection.

**Parameters:**
- `collection` (str): Output collection name

**Example:**
```python
AggregateBuilder()
    .group(by="$category", total={"$sum": "$amount"})
    .out("category_totals")
```

### merge(into: Union[str, Dict[str, Any]], on: Optional[Union[str, List[str]]] = None, when_matched: Optional[str] = None, when_not_matched: Optional[str] = None) -> AggregateBuilder

Merges pipeline results into a collection.

**Parameters:**
- `into` (Union[str, Dict[str, Any]]): Target collection
- `on` (Optional[Union[str, List[str]]]): Field(s) to match on
- `when_matched` (Optional[str]): Action for matches
- `when_not_matched` (Optional[str]): Action for non-matches

**Example:**
```python
AggregateBuilder().merge(
    into="summary_collection",
    on="_id",
    when_matched="merge",
    when_not_matched="insert"
)
```

### add_stage(stage: Dict[str, Any]) -> AggregateBuilder

Adds a custom stage to the pipeline.

**Parameters:**
- `stage` (Dict[str, Any]): Custom stage dictionary

**Example:**
```python
AggregateBuilder().add_stage({
    "$redact": {
        "$cond": {
            "if": {"$eq": ["$level", 5]},
            "then": "$$PRUNE",
            "else": "$$DESCEND"
        }
    }
})
```

## Advanced Usage

### Complex Aggregation Pipeline

```python
from mongodb_query_builder import AggregateBuilder, QueryFilter

pipeline = AggregateBuilder()
    # Filter active users
    .match(QueryFilter().field("status").equals("active"))
    
    # Join with orders collection
    .lookup(
        from_collection="orders",
        local_field="_id",
        foreign_field="userId",
        as_field="orders"
    )
    
    # Unwind orders array
    .unwind("$orders")
    
    # Group by user and calculate totals
    .group(
        by="$_id",
        name={"$first": "$name"},
        totalOrders={"$sum": 1},
        totalSpent={"$sum": "$orders.amount"},
        avgOrderValue={"$avg": "$orders.amount"}
    )
    
    # Add computed fields
    .add_fields(
        customerTier={
            "$switch": {
                "branches": [
                    {"case": {"$gte": ["$totalSpent", 10000]}, "then": "Platinum"},
                    {"case": {"$gte": ["$totalSpent", 5000]}, "then": "Gold"},
                    {"case": {"$gte": ["$totalSpent", 1000]}, "then": "Silver"}
                ],
                "default": "Bronze"
            }
        }
    )
    
    # Sort by total spent
    .sort("totalSpent", ascending=False)
    
    # Limit to top 100 customers
    .limit(100)
    
    # Build the pipeline
    .build()
```

### Faceted Search Pipeline

```python
search_pipeline = AggregateBuilder()
    # Initial match
    .match(QueryFilter().field("category").in_(["electronics", "computers"]))
    
    # Faceted aggregation
    .facet(
        # Main results
        products=[
            {"$sort": {"popularity": -1}},
            {"$skip": 0},
            {"$limit": 20},
            {"$project": {
                "name": 1,
                "price": 1,
                "image": 1,
                "rating": 1
            }}
        ],
        
        # Price ranges
        priceRanges=[
            {"$bucket": {
                "groupBy": "$price",
                "boundaries": [0, 100, 500, 1000, 5000],
                "default": "5000+",
                "output": {"count": {"$sum": 1}}
            }}
        ],
        
        # Brand counts
        brands=[
            {"$group": {"_id": "$brand", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ],
        
        # Total count
        totalCount=[
            {"$count": "total"}
        ]
    )
    .build()
```

### Time Series Aggregation

```python
time_series = AggregateBuilder()
    # Match date range
    .match(QueryFilter()
        .field("timestamp")
        .between(datetime(2024, 1, 1), datetime(2024, 12, 31))
    )
    
    # Group by time buckets
    .group(
        by={
            "year": {"$year": "$timestamp"},
            "month": {"$month": "$timestamp"},
            "day": {"$dayOfMonth": "$timestamp"}
        },
        dailyRevenue={"$sum": "$amount"},
        orderCount={"$sum": 1},
        avgOrderValue={"$avg": "$amount"}
    )
    
    # Calculate running totals
    .set(
        date={
            "$dateFromParts": {
                "year": "$_id.year",
                "month": "$_id.month",
                "day": "$_id.day"
            }
        }
    )
    
    # Sort by date
    .sort("date", ascending=True)
    
    # Add running total
    .set(
        runningTotal={
            "$sum": {
                "$slice": ["$dailyRevenue", {"$add": ["$$CURRENT.index", 1]}]
            }
        }
    )
    .build()
```

## Performance Considerations

1. **Stage Order Matters**: Place `$match` stages early to reduce documents
2. **Index Usage**: Ensure `$match` and `$sort` can use indexes
3. **Memory Limits**: Aggregations have a 100MB memory limit per stage
4. **Allow Disk Use**: For large datasets, enable disk usage
5. **Pipeline Optimization**: MongoDB optimizes certain stage sequences

## Error Handling

AggregateBuilder raises `AggregateBuilderError` for invalid operations:

```python
from mongodb_query_builder import AggregateBuilder, AggregateBuilderError

try:
    pipeline = AggregateBuilder()
        .limit(-1)  # Invalid limit value
        .build()
except AggregateBuilderError as e:
    print(f"Pipeline construction error: {e}")
```

## Integration with QueryFilter

```python
# Create reusable filters
active_filter = QueryFilter().field("status").equals("active")
recent_filter = QueryFilter().field("created").greater_than(datetime.now() - timedelta(days=30))

# Use in pipeline
pipeline = AggregateBuilder()
    .match(active_filter)
    .match(recent_filter)
    .group(by="$category", count={"$sum": 1})
    .build()
```

## See Also

- [QueryFilter](query-filter.md) - For building match conditions
- [AtlasSearchBuilder](atlas-search-builder.md) - For Atlas Search integration
- [Aggregation Tutorial](../tutorials/02-aggregation-pipelines.md) - Step-by-step guide
- [Performance Guide](../performance-guide.md) - Optimization tips
