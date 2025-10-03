"""
Unit tests for AtlasSearchBuilder, CompoundBuilder, and ClauseBuilder
"""

import pytest
from bson import ObjectId

from mongodb_query_builder import AtlasSearchBuilder, CompoundBuilder
from mongodb_query_builder.exceptions import AtlasSearchError


class TestCompoundBuilderBasics:
    """Test basic CompoundBuilder functionality"""

    def test_empty_compound(self, empty_compound_builder):
        """Test empty compound builder"""
        result = empty_compound_builder.build()
        assert result == {}

    def test_compound_must_clause(self):
        """Test must clause"""
        compound = CompoundBuilder()
        compound.must().text("python", path="skills")
        result = compound.build()
        assert "must" in result
        assert len(result["must"]) == 1

    def test_compound_should_clause(self):
        """Test should clause"""
        compound = CompoundBuilder()
        compound.should().text("senior", path="level")
        result = compound.build()
        assert "should" in result

    def test_compound_must_not_clause(self):
        """Test mustNot clause"""
        compound = CompoundBuilder()
        compound.must_not().equals("status", "inactive")
        result = compound.build()
        assert "mustNot" in result

    def test_compound_filter_clause(self):
        """Test filter clause"""
        compound = CompoundBuilder()
        compound.filter().range("age", gte=18)
        result = compound.build()
        assert "filter" in result

    def test_minimum_should_match(self):
        """Test minimum should match"""
        compound = CompoundBuilder()
        compound.should().text("python", path="skills")
        compound.should().text("java", path="skills")
        compound.minimum_should_match(1)
        result = compound.build()
        assert result["minimumShouldMatch"] == 1

    def test_minimum_should_match_negative_raises_error(self):
        """Test negative minimum should match raises error"""
        with pytest.raises(AtlasSearchError, match="non-negative"):
            CompoundBuilder().minimum_should_match(-1)


class TestCompoundBuilderMultipleClauses:
    """Test compound queries with multiple clauses"""

    def test_must_and_should(self, complex_compound_builder):
        """Test must and should together"""
        result = complex_compound_builder.build()
        assert "must" in result
        assert "should" in result
        assert len(result["must"]) > 0
        assert len(result["should"]) > 0

    def test_all_clause_types(self):
        """Test all clause types together"""
        compound = CompoundBuilder()
        compound.must().text("python", path="skills")
        compound.should().text("senior", path="level")
        compound.filter().range("experience", gte=3)
        compound.must_not().equals("status", "inactive")

        result = compound.build()
        assert "must" in result
        assert "should" in result
        assert "filter" in result
        assert "mustNot" in result

    def test_empty_clauses_omitted(self):
        """Test empty clauses are omitted from result"""
        compound = CompoundBuilder()
        compound.must().text("python", path="skills")
        result = compound.build()
        # Should only have 'must', not other empty clauses
        assert "must" in result
        assert "should" not in result
        assert "filter" not in result
        assert "mustNot" not in result


class TestClauseBuilderText:
    """Test text search clauses"""

    def test_text_simple(self):
        """Test simple text search"""
        compound = CompoundBuilder()
        compound.must().text("python", path="skills")
        result = compound.build()
        text_clause = result["must"][0]["text"]
        assert text_clause["query"] == "python"
        assert text_clause["path"] == "skills"

    def test_text_multiple_paths(self):
        """Test text search on multiple paths"""
        compound = CompoundBuilder()
        compound.must().text("python", path=["title", "content"])
        result = compound.build()
        assert result["must"][0]["text"]["path"] == ["title", "content"]

    def test_text_with_fuzzy(self):
        """Test text search with fuzzy matching"""
        compound = CompoundBuilder()
        compound.must().text("python", path="skills", fuzzy={"maxEdits": 1})
        result = compound.build()
        assert "fuzzy" in result["must"][0]["text"]
        assert result["must"][0]["text"]["fuzzy"]["maxEdits"] == 1

    def test_text_with_score(self):
        """Test text search with score boost"""
        compound = CompoundBuilder()
        compound.should().text("senior", path="level", score=2.0)
        result = compound.build()
        assert "score" in result["should"][0]["text"]
        assert result["should"][0]["text"]["score"]["boost"]["value"] == 2.0

    def test_text_empty_query_raises_error(self):
        """Test text with empty query raises error"""
        with pytest.raises(AtlasSearchError, match="cannot be empty"):
            compound = CompoundBuilder()
            compound.must().text("", path="skills")

    def test_text_empty_path_raises_error(self):
        """Test text with empty path raises error"""
        with pytest.raises(AtlasSearchError, match="requires a path"):
            compound = CompoundBuilder()
            compound.must().text("python", path="")


class TestClauseBuilderPhrase:
    """Test phrase search clauses"""

    def test_phrase_simple(self):
        """Test simple phrase search"""
        compound = CompoundBuilder()
        compound.must().phrase("machine learning", path="skills")
        result = compound.build()
        phrase = result["must"][0]["phrase"]
        assert phrase["query"] == "machine learning"
        assert phrase["slop"] == 0

    def test_phrase_with_slop(self):
        """Test phrase with slop"""
        compound = CompoundBuilder()
        compound.must().phrase("machine learning", path="skills", slop=2)
        result = compound.build()
        assert result["must"][0]["phrase"]["slop"] == 2

    def test_phrase_with_score(self):
        """Test phrase with score boost"""
        compound = CompoundBuilder()
        compound.should().phrase("exact phrase", path="content", score=3.0)
        result = compound.build()
        assert "score" in result["should"][0]["phrase"]


class TestClauseBuilderWildcard:
    """Test wildcard search clauses"""

    def test_wildcard_simple(self):
        """Test simple wildcard search"""
        compound = CompoundBuilder()
        compound.must().wildcard("test*", path="name")
        result = compound.build()
        wildcard = result["must"][0]["wildcard"]
        assert wildcard["query"] == "test*"
        assert wildcard["allowAnalyzedField"] is False

    def test_wildcard_allow_analyzed(self):
        """Test wildcard with analyzed field"""
        compound = CompoundBuilder()
        compound.must().wildcard("*test*", path="name", allow_analyzed_field=True)
        result = compound.build()
        assert result["must"][0]["wildcard"]["allowAnalyzedField"] is True


class TestClauseBuilderRegex:
    """Test regex search clauses"""

    def test_regex_simple(self):
        """Test simple regex search"""
        compound = CompoundBuilder()
        compound.must().regex("^test.*", path="name")
        result = compound.build()
        regex = result["must"][0]["regex"]
        assert regex["query"] == "^test.*"
        assert regex["allowAnalyzedField"] is False


class TestClauseBuilderRange:
    """Test range clauses"""

    def test_range_gte(self):
        """Test range with gte"""
        compound = CompoundBuilder()
        compound.filter().range("age", gte=18)
        result = compound.build()
        assert result["filter"][0]["range"]["gte"] == 18

    def test_range_lte(self):
        """Test range with lte"""
        compound = CompoundBuilder()
        compound.filter().range("age", lte=65)
        result = compound.build()
        assert result["filter"][0]["range"]["lte"] == 65

    def test_range_between(self):
        """Test range between two values"""
        compound = CompoundBuilder()
        compound.filter().range("age", gte=18, lte=65)
        result = compound.build()
        range_clause = result["filter"][0]["range"]
        assert range_clause["gte"] == 18
        assert range_clause["lte"] == 65

    def test_range_no_boundaries_raises_error(self):
        """Test range without boundaries raises error"""
        with pytest.raises(AtlasSearchError, match="must be provided"):
            compound = CompoundBuilder()
            compound.filter().range("age")


class TestClauseBuilderEquals:
    """Test equals clauses"""

    def test_equals_simple(self):
        """Test simple equals"""
        compound = CompoundBuilder()
        compound.must().equals("status", "active")
        result = compound.build()
        equals = result["must"][0]["equals"]
        assert equals["path"] == "status"
        assert equals["value"] == "active"

    def test_equals_with_objectid(self, sample_objectid):
        """Test equals with ObjectId"""
        compound = CompoundBuilder()
        compound.must().equals("_id", sample_objectid)
        result = compound.build()
        assert result["must"][0]["equals"]["value"] == sample_objectid


class TestClauseBuilderExists:
    """Test exists clauses"""

    def test_exists(self):
        """Test exists clause"""
        compound = CompoundBuilder()
        compound.filter().exists("email")
        result = compound.build()
        exists = result["filter"][0]["exists"]
        assert exists["path"] == "email"


class TestClauseBuilderAutocomplete:
    """Test autocomplete clauses"""

    def test_autocomplete_simple(self):
        """Test simple autocomplete"""
        compound = CompoundBuilder()
        compound.must().autocomplete("user i", path="username")
        result = compound.build()
        autocomplete = result["must"][0]["autocomplete"]
        assert autocomplete["query"] == "user i"
        assert autocomplete["path"] == "username"

    def test_autocomplete_with_fuzzy(self):
        """Test autocomplete with fuzzy"""
        compound = CompoundBuilder()
        compound.must().autocomplete("user i", path="username", fuzzy={"maxEdits": 2})
        result = compound.build()
        assert "fuzzy" in result["must"][0]["autocomplete"]


class TestClauseBuilderNested:
    """Test nested compound clauses"""

    def test_nested_compound(self):
        """Test nested compound query"""
        inner = CompoundBuilder()
        inner.should().text("python", path="skills")
        inner.should().text("java", path="skills")

        outer = CompoundBuilder()
        outer.must().compound(inner)

        result = outer.build()
        assert "compound" in result["must"][0]
        assert "should" in result["must"][0]["compound"]


class TestClauseBuilderRaw:
    """Test raw clauses"""

    def test_raw_clause(self):
        """Test adding raw clause"""
        compound = CompoundBuilder()
        compound.must().raw({"customOperator": {"field": "value"}})
        result = compound.build()
        assert "customOperator" in result["must"][0]

    def test_raw_empty_raises_error(self):
        """Test raw with empty dict raises error"""
        with pytest.raises(AtlasSearchError, match="non-empty clause"):
            compound = CompoundBuilder()
            compound.must().raw({})


class TestClauseBuilderChaining:
    """Test clause builder method chaining"""

    def test_chaining_within_clause(self):
        """Test chaining multiple conditions in same clause"""
        compound = CompoundBuilder()
        compound.must().text("python", path="skills").text("senior", path="level")
        result = compound.build()
        assert len(result["must"]) == 2

    def test_end_returns_to_compound(self):
        """Test end() returns to CompoundBuilder"""
        compound = CompoundBuilder()
        returned = compound.must().text("python", path="skills").end()
        assert isinstance(returned, CompoundBuilder)
        assert returned is compound


class TestAtlasSearchBuilderBasics:
    """Test basic AtlasSearchBuilder functionality"""

    def test_empty_search(self, empty_atlas_search_builder):
        """Test empty search builder"""
        result = empty_atlas_search_builder.build()
        assert "index" in result
        assert result["index"] == "default"

    def test_custom_index(self):
        """Test custom index name"""
        builder = AtlasSearchBuilder(index="custom_index")
        result = builder.build()
        assert result["index"] == "custom_index"

    def test_representation(self):
        """Test string representation"""
        builder = AtlasSearchBuilder(index="test")
        repr_str = repr(builder)
        assert "AtlasSearchBuilder" in repr_str
        assert "test" in repr_str


class TestAtlasSearchText:
    """Test text search operator"""

    def test_text_simple(self):
        """Test simple text search"""
        builder = AtlasSearchBuilder().text("python", path="skills")
        result = builder.build()
        assert "text" in result
        assert result["text"]["query"] == "python"
        assert result["text"]["path"] == "skills"

    def test_text_multiple_paths(self):
        """Test text on multiple paths"""
        builder = AtlasSearchBuilder().text("python", path=["title", "content"])
        result = builder.build()
        assert result["text"]["path"] == ["title", "content"]

    def test_text_with_fuzzy(self):
        """Test text with fuzzy matching"""
        builder = AtlasSearchBuilder().text("python", path="skills", fuzzy={"maxEdits": 1})
        result = builder.build()
        assert "fuzzy" in result["text"]


class TestAtlasSearchPhrase:
    """Test phrase search operator"""

    def test_phrase_simple(self):
        """Test simple phrase search"""
        builder = AtlasSearchBuilder().phrase("machine learning", path="content")
        result = builder.build()
        assert "phrase" in result
        assert result["phrase"]["query"] == "machine learning"


class TestAtlasSearchAutocomplete:
    """Test autocomplete operator"""

    def test_autocomplete_simple(self):
        """Test simple autocomplete"""
        builder = AtlasSearchBuilder().autocomplete("user i", path="username")
        result = builder.build()
        assert "autocomplete" in result
        assert result["autocomplete"]["query"] == "user i"
        assert result["autocomplete"]["tokenOrder"] == "sequential"

    def test_autocomplete_custom_max_terms(self):
        """Test autocomplete with custom maxTerms"""
        builder = AtlasSearchBuilder().autocomplete("user", path="username", max_terms=100)
        result = builder.build()
        assert result["autocomplete"]["maxTerms"] == 100


class TestAtlasSearchRegex:
    """Test regex operator"""

    def test_regex(self):
        """Test regex search"""
        builder = AtlasSearchBuilder().regex("^test.*", path="name")
        result = builder.build()
        assert "regex" in result
        assert result["regex"]["query"] == "^test.*"


class TestAtlasSearchWildcard:
    """Test wildcard operator"""

    def test_wildcard(self):
        """Test wildcard search"""
        builder = AtlasSearchBuilder().wildcard("test*", path="name")
        result = builder.build()
        assert "wildcard" in result
        assert result["wildcard"]["query"] == "test*"


class TestAtlasSearchRange:
    """Test range operator"""

    def test_range(self):
        """Test range search"""
        builder = AtlasSearchBuilder().range("price", gte=10, lte=100)
        result = builder.build()
        assert "range" in result
        assert result["range"]["gte"] == 10
        assert result["range"]["lte"] == 100


class TestAtlasSearchCompound:
    """Test compound operator"""

    def test_compound_integration(self):
        """Test integrating CompoundBuilder"""
        compound = CompoundBuilder()
        compound.must().text("python", path="skills")
        compound.should().text("senior", path="level")

        builder = AtlasSearchBuilder().compound(compound)
        result = builder.build()
        assert "compound" in result
        assert "must" in result["compound"]
        assert "should" in result["compound"]


class TestAtlasSearchFacet:
    """Test facet configuration"""

    def test_facet_string(self):
        """Test string facet"""
        builder = AtlasSearchBuilder().facet("categories", type="string", path="category")
        result = builder.build()
        assert "facets" in result
        assert result["facets"]["categories"]["type"] == "string"

    def test_facet_number_with_boundaries(self):
        """Test number facet with boundaries"""
        builder = AtlasSearchBuilder().facet(
            "price_ranges", type="number", path="price", boundaries=[0, 50, 100, 200]
        )
        result = builder.build()
        facet = result["facets"]["price_ranges"]
        assert facet["type"] == "number"
        assert facet["boundaries"] == [0, 50, 100, 200]

    def test_multiple_facets(self):
        """Test multiple facets"""
        builder = (
            AtlasSearchBuilder()
            .facet("categories", type="string", path="category")
            .facet("price_ranges", type="number", path="price", boundaries=[0, 100])
        )
        result = builder.build()
        assert len(result["facets"]) == 2


class TestAtlasSearchFacetOperator:
    """Test facet operator mode"""

    def test_facet_operator_with_compound(self):
        """Test facet operator with compound"""
        compound = CompoundBuilder()
        compound.must().equals("userId", ObjectId())

        builder = (
            AtlasSearchBuilder()
            .use_facet_operator(compound)
            .facet("types", type="string", path="type")
        )
        result = builder.build()
        assert "facet" in result
        assert "operator" in result["facet"]
        assert "facets" in result["facet"]

    def test_facet_operator_with_raw_dict(self):
        """Test facet operator with raw dict"""
        operator = {"text": {"query": "search", "path": "field"}}
        builder = (
            AtlasSearchBuilder()
            .use_facet_operator(operator)
            .facet("categories", type="string", path="category")
        )
        result = builder.build()
        assert result["facet"]["operator"] == operator


class TestAtlasSearchMoreLikeThis:
    """Test moreLikeThis operator"""

    def test_more_like_this_single(self):
        """Test moreLikeThis with single document"""
        doc = {"title": "Test", "content": "Content"}
        builder = AtlasSearchBuilder().more_like_this(like=doc)
        result = builder.build()
        assert "moreLikeThis" in result
        assert result["moreLikeThis"]["like"] == doc

    def test_more_like_this_multiple(self):
        """Test moreLikeThis with multiple documents"""
        docs = [{"title": "Test1"}, {"title": "Test2"}]
        builder = AtlasSearchBuilder().more_like_this(like=docs)
        result = builder.build()
        assert isinstance(result["moreLikeThis"]["like"], list)


class TestAtlasSearchScoreFunction:
    """Test score function"""

    def test_score_function_multiply(self):
        """Test multiply score function"""
        builder = AtlasSearchBuilder().score_function("multiply", factor=2.0)
        result = builder.build()
        assert "score" in result
        assert "multiply" in result["score"]["function"]


class TestAtlasSearchCount:
    """Test count configuration"""

    def test_count_lower_bound(self):
        """Test count with lowerBound"""
        builder = AtlasSearchBuilder().count(type="lowerBound")
        result = builder.build()
        assert result["count"]["type"] == "lowerBound"

    def test_count_total(self):
        """Test count with total"""
        builder = AtlasSearchBuilder().count(type="total")
        result = builder.build()
        assert result["count"]["type"] == "total"

    def test_count_with_threshold(self):
        """Test count with threshold"""
        builder = AtlasSearchBuilder().count(type="total", threshold=1000)
        result = builder.build()
        assert result["count"]["threshold"] == 1000


class TestAtlasSearchStages:
    """Test building aggregation stages"""

    def test_build_stage(self):
        """Test building $search stage"""
        builder = AtlasSearchBuilder().text("python", path="skills")
        result = builder.build_stage()
        assert "$search" in result
        assert "text" in result["$search"]

    def test_build_meta_stage(self):
        """Test building $searchMeta stage"""
        builder = AtlasSearchBuilder().text("python", path="skills")
        result = builder.build_meta_stage()
        assert "$searchMeta" in result
        assert "text" in result["$searchMeta"]


class TestAtlasSearchComplexQueries:
    """Test complex Atlas Search queries"""

    def test_full_search_query(self):
        """Test complete search query"""
        compound = CompoundBuilder()
        compound.must().text("python", path="skills")
        compound.should().text("senior", path="level", score=2.0)
        compound.filter().range("experience", gte=3)

        builder = (
            AtlasSearchBuilder(index="jobs")
            .compound(compound)
            .facet("companies", type="string", path="company")
            .count(type="total")
        )

        result = builder.build()
        assert "index" in result
        assert "compound" in result
        assert "facets" in result
        assert "count" in result

    def test_facet_operator_full(self):
        """Test complete facet operator query"""
        compound = CompoundBuilder()
        compound.must().equals("userId", ObjectId())
        compound.must().text("success", path="status")

        builder = (
            AtlasSearchBuilder(index="messages")
            .use_facet_operator(compound)
            .facet("types", type="string", path="type")
            .facet("dates", type="date", path="created_at")
        )

        result = builder.build()
        assert "facet" in result
        assert "operator" in result["facet"]
        assert "compound" in result["facet"]["operator"]
        assert len(result["facet"]["facets"]) == 2
