"""
Tests for the declarative search models module.
"""

import pytest

from mongodb_query_builder import (
    IndexField,
    SearchModel,
    SearchQuery,
    AtlasSearchBuilder,
    CompoundBuilder,
)


class TestIndexField:
    """Tests for IndexField configuration."""

    def test_string_index_field(self):
        """Test string index field configuration."""
        field = IndexField(string_index=True)
        assert field.is_searchable
        assert not field.is_facetable
        assert field.search_type == "string"
        assert field.facet_type is None

    def test_string_facet_field(self):
        """Test string facet field configuration."""
        field = IndexField(string_facet=True)
        assert not field.is_searchable
        assert field.is_facetable
        assert field.search_type is None
        assert field.facet_type == "string"

    def test_number_index_field(self):
        """Test number index field configuration."""
        field = IndexField(number_index=True)
        assert field.is_searchable
        assert not field.is_facetable
        assert field.search_type == "number"
        assert field.facet_type is None

    def test_number_facet_field(self):
        """Test number facet field configuration."""
        field = IndexField(number_facet=True)
        assert not field.is_searchable
        assert field.is_facetable
        assert field.search_type is None
        assert field.facet_type == "number"

    def test_date_index_field(self):
        """Test date index field configuration."""
        field = IndexField(date_index=True)
        assert field.is_searchable
        assert not field.is_facetable
        assert field.search_type == "date"
        assert field.facet_type is None

    def test_date_facet_field(self):
        """Test date facet field configuration."""
        field = IndexField(date_facet=True)
        assert not field.is_searchable
        assert field.is_facetable
        assert field.search_type is None
        assert field.facet_type == "date"

    def test_combined_index_and_facet(self):
        """Test field with both index and facet capabilities."""
        field = IndexField(string_index=True, string_facet=True)
        assert field.is_searchable
        assert field.is_facetable
        assert field.search_type == "string"
        assert field.facet_type == "string"

    def test_empty_field(self):
        """Test field with no configuration."""
        field = IndexField()
        assert not field.is_searchable
        assert not field.is_facetable
        assert field.search_type is None
        assert field.facet_type is None

    def test_repr(self):
        """Test field representation."""
        field = IndexField(string_index=True, number_facet=True)
        repr_str = repr(field)
        assert "IndexField" in repr_str
        assert "string_index=True" in repr_str
        assert "number_facet=True" in repr_str


class TestSearchModel:
    """Tests for SearchModel base class."""

    def test_basic_model_definition(self):
        """Test basic model with class attributes."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)
            age = IndexField(number_index=True)

        assert UserSearch.index == "users"
        assert "name" in UserSearch._fields
        assert "age" in UserSearch._fields
        assert isinstance(UserSearch._fields["name"], IndexField)

    def test_model_with_fields_dict(self):
        """Test model using fields dictionary for complex field names."""
        class MessageSearch(SearchModel):
            index = "messages"
            fields = {
                "type": IndexField(string_facet=True, string_index=True),
                "rawData.from": IndexField(string_index=True),
                "status": IndexField(string_index=True),
            }

        assert MessageSearch.index == "messages"
        assert "type" in MessageSearch._fields
        assert "rawData.from" in MessageSearch._fields
        assert "status" in MessageSearch._fields

    def test_model_with_combined_definition(self):
        """Test model with both class attributes and fields dict."""
        class ProductSearch(SearchModel):
            index = "products"
            name = IndexField(string_index=True)
            fields = {
                "price.amount": IndexField(number_index=True, number_facet=True),
                "category": IndexField(string_facet=True),
            }

        assert "name" in ProductSearch._fields
        assert "price.amount" in ProductSearch._fields
        assert "category" in ProductSearch._fields

    def test_get_field(self):
        """Test getting field configuration."""
        class UserSearch(SearchModel):
            name = IndexField(string_index=True)
            age = IndexField(number_index=True)

        field = UserSearch.get_field("name")
        assert field is not None
        assert field.string_index

        missing_field = UserSearch.get_field("nonexistent")
        assert missing_field is None

    def test_get_searchable_fields(self):
        """Test getting all searchable fields."""
        class UserSearch(SearchModel):
            name = IndexField(string_index=True)
            age = IndexField(number_index=True)
            status = IndexField(string_facet=True)  # facet only

        searchable = UserSearch.get_searchable_fields()
        assert "name" in searchable
        assert "age" in searchable
        assert "status" not in searchable

    def test_get_facetable_fields(self):
        """Test getting all facetable fields."""
        class UserSearch(SearchModel):
            name = IndexField(string_index=True)  # search only
            age = IndexField(number_facet=True)
            status = IndexField(string_facet=True)

        facetable = UserSearch.get_facetable_fields()
        assert "name" not in facetable
        assert "age" in facetable
        assert "status" in facetable

    def test_validate_field_success(self):
        """Test field validation for valid operations."""
        class UserSearch(SearchModel):
            name = IndexField(string_index=True)
            age = IndexField(number_facet=True)

        # Should not raise
        UserSearch.validate_field("name", "search")
        UserSearch.validate_field("age", "facet")

    def test_validate_field_missing(self):
        """Test validation for missing field."""
        class UserSearch(SearchModel):
            name = IndexField(string_index=True)

        with pytest.raises(ValueError, match="not defined"):
            UserSearch.validate_field("nonexistent", "search")

    def test_validate_field_wrong_operation(self):
        """Test validation for unsupported operation."""
        class UserSearch(SearchModel):
            name = IndexField(string_index=True)  # search only

        with pytest.raises(ValueError, match="not configured for faceting"):
            UserSearch.validate_field("name", "facet")

    def test_get_all_fields(self):
        """Test getting all field definitions."""
        class UserSearch(SearchModel):
            name = IndexField(string_index=True)
            age = IndexField(number_index=True)

        all_fields = UserSearch.get_all_fields()
        assert len(all_fields) == 2
        assert "name" in all_fields
        assert "age" in all_fields

    def test_builder_method(self):
        """Test getting a raw builder."""
        class UserSearch(SearchModel):
            index = "users"

        builder = UserSearch.builder()
        assert isinstance(builder, AtlasSearchBuilder)

    def test_search_method(self):
        """Test starting a search query."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)

        query = UserSearch.search()
        assert isinstance(query, SearchQuery)
        assert query.model_class == UserSearch


class TestSearchQuery:
    """Tests for SearchQuery builder."""

    def test_text_search(self):
        """Test text search query."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)

        result = UserSearch.search().text("john", field="name").build()
        
        assert result["index"] == "users"
        assert "text" in result
        assert result["text"]["query"] == "john"

    def test_text_search_with_fuzzy(self):
        """Test text search with fuzzy matching."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)

        fuzzy = {"maxEdits": 2}
        result = UserSearch.search().text("john", field="name", fuzzy=fuzzy).build()
        
        assert result["text"]["fuzzy"] == fuzzy

    def test_text_search_invalid_field(self):
        """Test text search on non-string field raises error."""
        class UserSearch(SearchModel):
            index = "users"
            age = IndexField(number_index=True)

        with pytest.raises(ValueError, match="must have string_index=True"):
            UserSearch.search().text("test", field="age")

    def test_phrase_search(self):
        """Test phrase search query."""
        class UserSearch(SearchModel):
            index = "users"
            bio = IndexField(string_index=True)

        result = UserSearch.search().phrase("software engineer", field="bio").build()
        
        assert "phrase" in result
        assert result["phrase"]["query"] == "software engineer"

    def test_autocomplete_search(self):
        """Test autocomplete query."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)

        result = UserSearch.search().autocomplete("joh", field="name").build()
        
        assert "autocomplete" in result
        assert result["autocomplete"]["query"] == "joh"

    def test_facet(self):
        """Test facet query."""
        class UserSearch(SearchModel):
            index = "users"
            category = IndexField(string_facet=True)

        result = UserSearch.search().facet("category").build()
        
        assert "facets" in result
        assert "category" in result["facets"]

    def test_facet_invalid_field(self):
        """Test facet on non-facetable field raises error."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)  # search only

        with pytest.raises(ValueError, match="not configured for faceting"):
            UserSearch.search().facet("name")

    def test_facet_all(self):
        """Test adding facets for all facetable fields."""
        class UserSearch(SearchModel):
            index = "users"
            category = IndexField(string_facet=True)
            age = IndexField(number_facet=True)
            name = IndexField(string_index=True)  # not facetable

        result = UserSearch.search().facet_all().build()
        
        assert "facets" in result
        assert "category" in result["facets"]
        assert "age" in result["facets"]
        assert "name" not in result["facets"]

    def test_compound_query(self):
        """Test compound query builder."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)

        compound = CompoundBuilder()
        compound.must().text("john", path="name")
        result = UserSearch.search().compound(compound).build()
        
        assert "compound" in result
        assert "must" in result["compound"]

    def test_count(self):
        """Test count configuration."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)

        result = (
            UserSearch.search()
            .text("john", field="name")
            .count(type="total", threshold=1000)
            .build()
        )
        
        assert "count" in result
        assert result["count"]["type"] == "total"

    def test_use_facet_operator(self):
        """Test facet operator mode."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)
            category = IndexField(string_facet=True)

        compound = CompoundBuilder()
        compound.must().text("john", path="name")
        result = (
            UserSearch.search()
            .use_facet_operator(compound)
            .facet("category")
            .build()
        )
        
        assert "facet" in result
        assert "operator" in result["facet"]

    def test_raw_builder_access(self):
        """Test accessing the underlying builder."""
        class UserSearch(SearchModel):
            index = "users"

        query = UserSearch.search()
        builder = query.raw_builder()
        
        assert isinstance(builder, AtlasSearchBuilder)

    def test_build_stage(self):
        """Test building as aggregation stage."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)

        result = UserSearch.search().text("john", field="name").build_stage()
        
        assert "$search" in result

    def test_build_meta_stage(self):
        """Test building as $searchMeta stage."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)

        result = UserSearch.search().text("john", field="name").build_meta_stage()
        
        assert "$searchMeta" in result

    def test_chaining(self):
        """Test method chaining."""
        class UserSearch(SearchModel):
            index = "users"
            name = IndexField(string_index=True)
            age = IndexField(number_facet=True)

        result = (
            UserSearch.search()
            .text("john", field="name")
            .facet("age")
            .count(type="total")
            .build()
        )
        
        assert "text" in result
        assert "facets" in result
        assert "count" in result


class TestComplexSearchModels:
    """Tests for complex real-world search model scenarios."""

    def test_message_search_model(self):
        """Test a complex message search model."""
        class MessageSearch(SearchModel):
            index = "messages"
            fields = {
                "type": IndexField(string_facet=True, string_index=True),
                "rawData.from": IndexField(string_facet=True, string_index=True),
                "rawData.to": IndexField(string_index=True),
                "status": IndexField(string_index=True),
                "timestamp": IndexField(date_index=True, date_facet=True),
            }

        # Should be able to search and facet on type
        result = (
            MessageSearch.search()
            .text("email", field="type")
            .facet("type")
            .build()
        )
        assert "text" in result
        assert "facets" in result

        # Should be able to search on nested fields
        result = (
            MessageSearch.search()
            .text("user@example.com", field="rawData.from")
            .build()
        )
        assert "text" in result

    def test_product_catalog_search(self):
        """Test product catalog search with mixed fields."""
        class ProductSearch(SearchModel):
            index = "products"
            name = IndexField(string_index=True)
            description = IndexField(string_index=True)
            category = IndexField(string_facet=True, string_index=True)
            fields = {
                "price.amount": IndexField(number_index=True, number_facet=True),
                "price.currency": IndexField(string_facet=True),
                "metadata.brand": IndexField(string_facet=True, string_index=True),
                "metadata.tags": IndexField(string_index=True),
            }

        # Complex query with multiple operations
        compound = CompoundBuilder()
        compound.must().text("laptop", path="name")
        compound.filter().text("electronics", path="category")

        result = (
            ProductSearch.search()
            .compound(compound)
            .facet("category")
            .facet("price.amount", boundaries=[0, 500, 1000, 2000])
            .facet("metadata.brand")
            .count(type="total")
            .build()
        )
        
        assert "compound" in result
        assert "facets" in result

    def test_user_search_autocomplete(self):
        """Test user search with autocomplete."""
        class UserSearch(SearchModel):
            index = "users"
            username = IndexField(string_index=True)
            email = IndexField(string_index=True)
            role = IndexField(string_facet=True)
            department = IndexField(string_facet=True)

        # Autocomplete on username
        result = (
            UserSearch.search()
            .autocomplete("joh", field="username")
            .facet_all()
            .build()
        )
        
        assert "autocomplete" in result
        assert "facets" in result
