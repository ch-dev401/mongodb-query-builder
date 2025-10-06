# Tutorial 1: Basic Queries with MongoDB Query Builder

In this tutorial, you'll learn how to use MongoDB Query Builder to create basic queries. We'll start with simple examples and gradually build more complex queries.

## Prerequisites

- Python 3.8 or higher installed
- MongoDB Query Builder installed (`pip install mongodb-query-builder`)
- Basic understanding of MongoDB query concepts

## Setting Up

First, let's import the necessary components:

```python
from mongodb_query_builder import QueryFilter
from pymongo import MongoClient

# Connect to MongoDB (optional - for running queries)
client = MongoClient("mongodb://localhost:27017/")
db = client["tutorial_db"]
collection = db["users"]
```

## Lesson 1: Simple Equality Queries

The most basic query checks if a field equals a specific value.

### Example: Find Active Users

```python
# Build the query
query = QueryFilter()
    .field("status").equals("active")
    .build()

print(query)
# Output: {"status": "active"}

# Use with PyMongo
active_users = collection.find(query)
```

### Example: Find Users by Age

```python
query = QueryFilter()
    .field("age").equals(25)
    .build()

# Output: {"age": 25}
```

## Lesson 2: Comparison Operators

MongoDB Query Builder supports all standard comparison operators.

### Greater Than / Less Than

```python
# Find users older than 18
query = QueryFilter()
    .field("age").greater_than(18)
    .build()
# Output: {"age": {"$gt": 18}}

# Find products under $50
query = QueryFilter()
    .field("price").less_than(50)
    .build()
# Output: {"price": {"$lt": 50}}
```

### Greater/Less Than or Equal

```python
# Find users 18 or older
query = QueryFilter()
    .field("age").greater_than_or_equal(18)
    .build()
# Output: {"age": {"$gte": 18}}

# Find items with 10 or fewer in stock
query = QueryFilter()
    .field("stock").less_than_or_equal(10)
    .build()
# Output: {"stock": {"$lte": 10}}
```

### Between (Range Queries)

```python
# Find users between 25 and 35 years old
query = QueryFilter()
    .field("age").between(25, 35)
    .build()
# Output: {"age": {"$gte": 25, "$lte": 35}}

# Find products in a price range
query = QueryFilter()
    .field("price").between(100, 500)
    .build()
# Output: {"price": {"$gte": 100, "$lte": 500}}
```

## Lesson 3: Working with Multiple Fields

You can query multiple fields by chaining field operations.

### Example: Multiple Conditions

```python
# Find active users over 18
query = QueryFilter()
    .field("status").equals("active")
    .field("age").greater_than(18)
    .build()

print(query)
# Output: {"status": "active", "age": {"$gt": 18}}
```

### Example: Complex User Query

```python
# Find premium users in New York aged 25-40
query = QueryFilter()
    .field("account_type").equals("premium")
    .field("city").equals("New York")
    .field("age").between(25, 40)
    .build()

# Output: {
#     "account_type": "premium",
#     "city": "New York",
#     "age": {"$gte": 25, "$lte": 40}
# }
```

## Lesson 4: Array Operations

MongoDB Query Builder provides methods for querying array fields.

### Checking Array Contents

```python
# Find users with "python" in their skills
query = QueryFilter()
    .field("skills").array_contains("python")
    .build()
# Output: {"skills": "python"}

# Find users with multiple specific skills
query = QueryFilter()
    .field("skills").array_contains_all(["python", "mongodb", "javascript"])
    .build()
# Output: {"skills": {"$all": ["python", "mongodb", "javascript"]}}
```

### Array Size

```python
# Find users with exactly 3 hobbies
query = QueryFilter()
    .field("hobbies").array_size(3)
    .build()
# Output: {"hobbies": {"$size": 3}}
```

## Lesson 5: String Operations

Query text fields with string-specific operations.

### Pattern Matching

```python
# Find users whose name starts with "John"
query = QueryFilter()
    .field("name").starts_with("John")
    .build()
# Output: {"name": {"$regex": "^John"}}

# Find emails ending with "@example.com"
query = QueryFilter()
    .field("email").ends_with("@example.com")
    .build()
# Output: {"email": {"$regex": "@example\\.com$"}}

# Find descriptions containing "python" (case-insensitive)
query = QueryFilter()
    .field("description").contains("python", case_sensitive=False)
    .build()
# Output: {"description": {"$regex": "python", "$options": "i"}}
```

### Regular Expressions

```python
# Find usernames matching a pattern
query = QueryFilter()
    .field("username").regex(r"^user_\d{4}$")
    .build()
# Output: {"username": {"$regex": "^user_\\d{4}$"}}
```

## Lesson 6: Logical Operators

Combine multiple conditions using logical operators.

### OR Conditions

```python
# Find users who are either admins or moderators
query = QueryFilter().any_of([
    QueryFilter().field("role").equals("admin"),
    QueryFilter().field("role").equals("moderator")
]).build()

# Output: {"$or": [{"role": "admin"}, {"role": "moderator"}]}
```

### AND Conditions (Explicit)

```python
# Find active premium users
query = QueryFilter().all_of([
    QueryFilter().field("status").equals("active"),
    QueryFilter().field("account_type").equals("premium")
]).build()

# Output: {"$and": [{"status": "active"}, {"account_type": "premium"}]}
```

### Complex Logical Combinations

```python
# Find active users who are either premium or have high engagement
query = QueryFilter().all_of([
    QueryFilter().field("status").equals("active"),
    QueryFilter().any_of([
        QueryFilter().field("account_type").equals("premium"),
        QueryFilter().field("engagement_score").greater_than(80)
    ])
]).build()

# Output: {
#     "$and": [
#         {"status": "active"},
#         {"$or": [
#             {"account_type": "premium"},
#             {"engagement_score": {"$gt": 80}}
#         ]}
#     ]
# }
```

## Lesson 7: Checking Field Existence

Query based on whether fields exist in documents.

```python
# Find users with an email address
query = QueryFilter()
    .field("email").exists()
    .build()
# Output: {"email": {"$exists": true}}

# Find users without a middle name
query = QueryFilter()
    .field("middle_name").exists(False)
    .build()
# Output: {"middle_name": {"$exists": false}}
```

## Lesson 8: Working with Nested Fields

Query nested document fields using dot notation.

```python
# Find users in New York
query = QueryFilter()
    .field("address.city").equals("New York")
    .build()
# Output: {"address.city": "New York"}

# Complex nested query
query = QueryFilter()
    .field("address.city").equals("San Francisco")
    .field("address.zipcode").starts_with("94")
    .field("profile.verified").equals(True)
    .build()

# Output: {
#     "address.city": "San Francisco",
#     "address.zipcode": {"$regex": "^94"},
#     "profile.verified": true
# }
```

## Practical Examples

### Example 1: E-commerce Product Search

```python
def find_discounted_electronics(min_discount=0.1, max_price=1000):
    """Find electronic products on sale."""
    return QueryFilter()
        .field("category").equals("electronics")
        .field("discount").greater_than_or_equal(min_discount)
        .field("price").less_than_or_equal(max_price)
        .field("in_stock").equals(True)
        .build()

# Usage
query = find_discounted_electronics(min_discount=0.2, max_price=500)
products = collection.find(query)
```

### Example 2: User Search with Multiple Criteria

```python
def find_qualified_users(min_age=21, required_skills=None, locations=None):
    """Find users matching job requirements."""
    query = QueryFilter()
        .field("age").greater_than_or_equal(min_age)
        .field("profile_complete").equals(True)
    
    if required_skills:
        query.field("skills").array_contains_all(required_skills)
    
    if locations:
        query.field("location").in_(locations)
    
    return query.build()

# Usage
query = find_qualified_users(
    min_age=25,
    required_skills=["python", "mongodb"],
    locations=["New York", "San Francisco", "Austin"]
)
```

### Example 3: Content Filtering

```python
def find_recent_posts(days=7, min_likes=10, tags=None):
    """Find popular recent posts."""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    query = QueryFilter()
        .field("created_at").greater_than_or_equal(cutoff_date)
        .field("likes").greater_than_or_equal(min_likes)
        .field("status").equals("published")
    
    if tags:
        query.field("tags").array_contains(tags[0])
    
    return query.build()

# Usage
query = find_recent_posts(days=3, min_likes=50, tags=["mongodb"])
```

## Best Practices

### 1. Use Type-Appropriate Methods

```python
# Good: Using numeric comparison for numbers
query = QueryFilter().field("age").greater_than(18)

# Bad: Using string methods for numbers
# query = QueryFilter().field("age").starts_with("1")  # Don't do this!
```

### 2. Build Reusable Query Functions

```python
def active_users_filter():
    """Reusable filter for active users."""
    return QueryFilter().field("status").equals("active")

def verified_users_filter():
    """Reusable filter for verified users."""
    return QueryFilter()
        .field("email_verified").equals(True)
        .field("phone_verified").equals(True)

# Combine filters
query = QueryFilter().all_of([
    active_users_filter(),
    verified_users_filter()
]).build()
```

### 3. Handle Optional Parameters

```python
def build_user_query(status=None, min_age=None, city=None):
    """Build a query with optional parameters."""
    query = QueryFilter()
    
    if status:
        query.field("status").equals(status)
    
    if min_age is not None:
        query.field("age").greater_than_or_equal(min_age)
    
    if city:
        query.field("address.city").equals(city)
    
    return query.build()
```

## Exercises

### Exercise 1: Product Catalog
Create a query to find all products that:
- Are in the "books" category
- Cost between $10 and $50
- Have a rating of 4 or higher
- Are currently in stock

<details>
<summary>Solution</summary>

```python
query = QueryFilter()
    .field("category").equals("books")
    .field("price").between(10, 50)
    .field("rating").greater_than_or_equal(4)
    .field("in_stock").equals(True)
    .build()
```
</details>

### Exercise 2: User Matching
Create a query to find users who:
- Are between 25 and 40 years old
- Live in either "London", "Paris", or "Berlin"
- Have "python" in their skills
- Have verified their email

<details>
<summary>Solution</summary>

```python
query = QueryFilter()
    .field("age").between(25, 40)
    .field("city").in_(["London", "Paris", "Berlin"])
    .field("skills").array_contains("python")
    .field("email_verified").equals(True)
    .build()
```
</details>

### Exercise 3: Complex Search
Create a query to find blog posts that:
- Were created in the last 30 days
- Have either more than 100 likes OR are featured
- Contain the tag "tutorial"
- Have a title starting with "How to"

<details>
<summary>Solution</summary>

```python
from datetime import datetime, timedelta

thirty_days_ago = datetime.now() - timedelta(days=30)

query = QueryFilter()
    .field("created_at").greater_than_or_equal(thirty_days_ago)
    .field("tags").array_contains("tutorial")
    .field("title").starts_with("How to")
    .any_of([
        QueryFilter().field("likes").greater_than(100),
        QueryFilter().field("featured").equals(True)
    ])
    .build()
```
</details>

## Summary

In this tutorial, you learned how to:
- Create simple equality queries
- Use comparison operators for numeric and date fields
- Query multiple fields in a single operation
- Work with arrays and string patterns
- Combine conditions using logical operators
- Query nested document fields
- Build reusable query functions

## Next Steps

- Continue to [Tutorial 2: Aggregation Pipelines](02-aggregation-pipelines.md)
- Explore the [QueryFilter API Reference](../api/query-filter.md)
- Try building queries for your own data models
- Learn about performance optimization in the [Performance Guide](../performance-guide.md)
