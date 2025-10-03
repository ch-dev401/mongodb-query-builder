"""
Unit tests for QueryFilter builder
"""

from datetime import datetime

import pytest
from bson import ObjectId

from mongodb_query_builder import QueryFilter
from mongodb_query_builder.exceptions import QueryFilterError


class TestQueryFilterBasics:
    """Test basic QueryFilter functionality"""

    def test_empty_filter(self, empty_query_filter):
        """Test empty filter builds to empty dict"""
        result = empty_query_filter.build()
        assert result == {}

    def test_filter_representation(self, simple_query_filter):
        """Test QueryFilter string representation"""
        repr_str = repr(simple_query_filter)
        assert "QueryFilter" in repr_str
        assert "status" in repr_str


class TestQueryFilterEquality:
    """Test equality operations"""

    def test_equals(self):
        """Test equals operation"""
        query = QueryFilter().field("status").equals("active")
        assert query.build() == {"status": "active"}

    def test_equals_with_objectid_string(self):
        """Test equals with ObjectId string auto-conversion"""
        oid_str = "507f1f77bcf86cd799439011"
        query = QueryFilter().field("_id").equals(oid_str)
        result = query.build()
        assert isinstance(result["_id"], ObjectId)
        assert str(result["_id"]) == oid_str

    def test_not_equals(self):
        """Test not equals operation"""
        query = QueryFilter().field("status").not_equals("inactive")
        assert query.build() == {"status": {"$ne": "inactive"}}

    def test_field_shorthand(self):
        """Test field shorthand with direct value"""
        query = QueryFilter().field("status", "active")
        assert query.build() == {"status": "active"}


class TestQueryFilterComparison:
    """Test comparison operations"""

    def test_greater_than(self):
        """Test greater than operation"""
        query = QueryFilter().field("age").greater_than(18)
        assert query.build() == {"age": {"$gt": 18}}

    def test_greater_than_or_equal(self):
        """Test greater than or equal operation"""
        query = QueryFilter().field("age").greater_than_or_equal(18)
        assert query.build() == {"age": {"$gte": 18}}

    def test_less_than(self):
        """Test less than operation"""
        query = QueryFilter().field("age").less_than(65)
        assert query.build() == {"age": {"$lt": 65}}

    def test_less_than_or_equal(self):
        """Test less than or equal operation"""
        query = QueryFilter().field("age").less_than_or_equal(65)
        assert query.build() == {"age": {"$lte": 65}}

    def test_between_inclusive(self):
        """Test between operation (inclusive)"""
        query = QueryFilter().field("age").between(18, 65, inclusive=True)
        assert query.build() == {"age": {"$gte": 18, "$lte": 65}}

    def test_between_exclusive(self):
        """Test between operation (exclusive)"""
        query = QueryFilter().field("age").between(18, 65, inclusive=False)
        assert query.build() == {"age": {"$gt": 18, "$lt": 65}}

    def test_between_with_datetime(self, sample_date_range):
        """Test between with datetime values"""
        query = (
            QueryFilter()
            .field("created_at")
            .between(sample_date_range["start"], sample_date_range["end"])
        )
        result = query.build()
        assert "$gte" in result["created_at"]
        assert "$lte" in result["created_at"]
        assert isinstance(result["created_at"]["$gte"], datetime)


class TestQueryFilterList:
    """Test list operations"""

    def test_in_list(self):
        """Test in list operation"""
        query = QueryFilter().field("status").in_list(["active", "pending"])
        assert query.build() == {"status": {"$in": ["active", "pending"]}}

    def test_in_list_with_objectid_strings(self):
        """Test in list with ObjectId string auto-conversion"""
        oid_strs = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
        query = QueryFilter().field("_id").in_list(oid_strs)
        result = query.build()
        assert all(isinstance(oid, ObjectId) for oid in result["_id"]["$in"])

    def test_in_list_empty_raises_error(self):
        """Test in list with empty list raises error"""
        with pytest.raises(QueryFilterError, match="cannot be empty"):
            QueryFilter().field("status").in_list([]).build()

    def test_not_in_list(self):
        """Test not in list operation"""
        query = QueryFilter().field("status").not_in_list(["inactive", "banned"])
        assert query.build() == {"status": {"$nin": ["inactive", "banned"]}}

    def test_not_in_list_empty_raises_error(self):
        """Test not in list with empty list raises error"""
        with pytest.raises(QueryFilterError, match="cannot be empty"):
            QueryFilter().field("status").not_in_list([]).build()


class TestQueryFilterString:
    """Test string operations"""

    def test_contains_case_insensitive(self):
        """Test contains operation (case insensitive)"""
        query = QueryFilter().field("name").contains("john", case_sensitive=False)
        result = query.build()
        assert result == {"name": {"$regex": "john", "$options": "i"}}

    def test_contains_case_sensitive(self):
        """Test contains operation (case sensitive)"""
        query = QueryFilter().field("name").contains("John", case_sensitive=True)
        result = query.build()
        assert result == {"name": {"$regex": "John", "$options": ""}}

    def test_starts_with(self):
        """Test starts with operation"""
        query = QueryFilter().field("name").starts_with("Jo")
        result = query.build()
        assert result["name"]["$regex"] == "^Jo"
        assert result["name"]["$options"] == "i"

    def test_ends_with(self):
        """Test ends with operation"""
        query = QueryFilter().field("name").ends_with("son")
        result = query.build()
        assert result["name"]["$regex"] == "son$"
        assert result["name"]["$options"] == "i"

    def test_regex(self):
        """Test custom regex operation"""
        query = QueryFilter().field("email").regex(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        result = query.build()
        assert "$regex" in result["email"]

    def test_regex_with_flags(self):
        """Test regex with flags"""
        query = QueryFilter().field("name").regex("pattern", flags="im")
        result = query.build()
        assert result["name"]["$options"] == "im"


class TestQueryFilterExistence:
    """Test field existence operations"""

    def test_exists_true(self):
        """Test exists operation (field should exist)"""
        query = QueryFilter().field("email").exists(True)
        assert query.build() == {"email": {"$exists": True}}

    def test_exists_false(self):
        """Test exists operation (field should not exist)"""
        query = QueryFilter().field("deleted_at").exists(False)
        assert query.build() == {"deleted_at": {"$exists": False}}

    def test_is_null(self):
        """Test is null operation"""
        query = QueryFilter().field("middle_name").is_null()
        assert query.build() == {"middle_name": None}

    def test_is_not_null(self):
        """Test is not null operation"""
        query = QueryFilter().field("email").is_not_null()
        assert query.build() == {"email": {"$ne": None}}


class TestQueryFilterArray:
    """Test array operations"""

    def test_array_contains(self):
        """Test array contains value"""
        query = QueryFilter().field("tags").array_contains("python")
        assert query.build() == {"tags": "python"}

    def test_array_contains_all(self):
        """Test array contains all values"""
        query = QueryFilter().field("tags").array_contains_all(["python", "mongodb"])
        assert query.build() == {"tags": {"$all": ["python", "mongodb"]}}

    def test_array_contains_all_empty_raises_error(self):
        """Test array contains all with empty list raises error"""
        with pytest.raises(QueryFilterError, match="cannot be empty"):
            QueryFilter().field("tags").array_contains_all([]).build()

    def test_array_size(self):
        """Test array size operation"""
        query = QueryFilter().field("tags").array_size(3)
        assert query.build() == {"tags": {"$size": 3}}

    def test_array_size_negative_raises_error(self):
        """Test array size with negative value raises error"""
        with pytest.raises(QueryFilterError, match="non-negative"):
            QueryFilter().field("tags").array_size(-1).build()

    def test_elem_match_with_dict(self):
        """Test elem match with dictionary"""
        conditions = {"price": {"$gt": 100}, "quantity": {"$gte": 2}}
        query = QueryFilter().field("items").elem_match(conditions)
        assert query.build() == {"items": {"$elemMatch": conditions}}

    def test_elem_match_with_query_filter(self):
        """Test elem match with QueryFilter"""
        conditions = QueryFilter().field("price").greater_than(100)
        query = QueryFilter().field("items").elem_match(conditions)
        result = query.build()
        assert "$elemMatch" in result["items"]
        assert "$gt" in result["items"]["$elemMatch"]["price"]


class TestQueryFilterLogical:
    """Test logical operations"""

    def test_any_of(self):
        """Test OR operation"""
        filters = [
            QueryFilter().field("role").equals("admin"),
            QueryFilter().field("role").equals("moderator"),
        ]
        query = QueryFilter().any_of(filters)
        result = query.build()
        assert "$or" in result
        assert len(result["$or"]) == 2

    def test_any_of_empty_raises_error(self):
        """Test any_of with empty list raises error"""
        with pytest.raises(QueryFilterError, match="cannot be empty"):
            QueryFilter().any_of([]).build()

    def test_all_of(self):
        """Test AND operation"""
        filters = [
            QueryFilter().field("age").greater_than(18),
            QueryFilter().field("status").equals("active"),
        ]
        query = QueryFilter().all_of(filters)
        result = query.build()
        assert "$and" in result
        assert len(result["$and"]) == 2

    def test_all_of_empty_raises_error(self):
        """Test all_of with empty list raises error"""
        with pytest.raises(QueryFilterError, match="cannot be empty"):
            QueryFilter().all_of([]).build()

    def test_none_of(self):
        """Test NOR operation"""
        filters = [
            QueryFilter().field("status").equals("inactive"),
            QueryFilter().field("status").equals("banned"),
        ]
        query = QueryFilter().none_of(filters)
        result = query.build()
        assert "$nor" in result
        assert len(result["$nor"]) == 2

    def test_none_of_empty_raises_error(self):
        """Test none_of with empty list raises error"""
        with pytest.raises(QueryFilterError, match="cannot be empty"):
            QueryFilter().none_of([]).build()

    def test_not_filter(self):
        """Test NOT operation"""
        inner_filter = QueryFilter().field("age").less_than(18)
        query = QueryFilter().not_filter(inner_filter)
        result = query.build()
        assert "$not" in result


class TestQueryFilterRaw:
    """Test raw filter operations"""

    def test_raw_filter(self):
        """Test adding raw MongoDB filter"""
        query = QueryFilter().raw({"custom_field": {"$custom": "value"}})
        result = query.build()
        assert "custom_field" in result
        assert result["custom_field"]["$custom"] == "value"

    def test_text_search(self):
        """Test full text search"""
        query = QueryFilter().text_search("python programming")
        result = query.build()
        assert "$text" in result
        assert result["$text"]["$search"] == "python programming"

    def test_text_search_with_language(self):
        """Test text search with language"""
        query = QueryFilter().text_search("python", language="en")
        result = query.build()
        assert result["$text"]["$language"] == "en"

    def test_text_search_case_sensitive(self):
        """Test case-sensitive text search"""
        query = QueryFilter().text_search("Python", case_sensitive=True)
        result = query.build()
        assert result["$text"]["$caseSensitive"] is True


class TestQueryFilterChaining:
    """Test method chaining"""

    def test_multiple_conditions(self):
        """Test chaining multiple conditions"""
        query = (
            QueryFilter()
            .field("age")
            .between(18, 65)
            .field("status")
            .equals("active")
            .field("email")
            .exists(True)
        )
        result = query.build()
        assert len(result) == 3
        assert "age" in result
        assert "status" in result
        assert "email" in result

    def test_complex_chaining(self):
        """Test complex chaining scenario"""
        query = (
            QueryFilter()
            .field("name")
            .starts_with("John")
            .field("age")
            .greater_than(18)
            .field("tags")
            .array_contains("python")
            .field("status")
            .in_list(["active", "pending"])
        )
        result = query.build()
        assert len(result) == 4


class TestQueryFilterErrors:
    """Test error handling"""

    def test_no_field_selected_error(self):
        """Test error when no field is selected"""
        with pytest.raises(QueryFilterError, match="No field selected"):
            QueryFilter().equals("value")

    def test_empty_field_name_error(self):
        """Test error with empty field name"""
        with pytest.raises(QueryFilterError, match="cannot be empty"):
            QueryFilter().field("").equals("value")

    def test_validation_error_messages_are_clear(self):
        """Test that validation error messages are clear"""
        try:
            QueryFilter().field("status").in_list([])
        except QueryFilterError as e:
            assert "cannot be empty" in str(e)
            assert "in_list" in str(e)


class TestQueryFilterEdgeCases:
    """Test edge cases"""

    def test_objectid_in_multiple_formats(self, sample_objectid):
        """Test ObjectId handling in various contexts"""
        # As string
        q1 = QueryFilter().field("_id").equals(str(sample_objectid))
        assert isinstance(q1.build()["_id"], ObjectId)

        # As ObjectId
        q2 = QueryFilter().field("_id").equals(sample_objectid)
        assert isinstance(q2.build()["_id"], ObjectId)

        # In list
        q3 = QueryFilter().field("_id").in_list([str(sample_objectid)])
        assert isinstance(q3.build()["_id"]["$in"][0], ObjectId)

    def test_datetime_comparison(self, sample_datetime):
        """Test datetime in comparisons"""
        query = QueryFilter().field("created_at").greater_than(sample_datetime)
        result = query.build()
        assert isinstance(result["created_at"]["$gt"], datetime)

    def test_special_characters_in_regex(self):
        """Test special characters are handled in regex"""
        query = QueryFilter().field("email").regex(r".*@example\.com$")
        result = query.build()
        assert r".*@example\.com$" in result["email"]["$regex"]

    def test_none_value_handling(self):
        """Test None value handling"""
        query = QueryFilter().field("optional_field").is_null()
        assert query.build() == {"optional_field": None}

    def test_boolean_values(self):
        """Test boolean value handling"""
        query = QueryFilter().field("is_active").equals(True)
        assert query.build() == {"is_active": True}

    def test_numeric_types(self):
        """Test different numeric types"""
        q1 = QueryFilter().field("count").equals(42)
        assert q1.build() == {"count": 42}

        q2 = QueryFilter().field("price").equals(19.99)
        assert q2.build() == {"price": 19.99}
