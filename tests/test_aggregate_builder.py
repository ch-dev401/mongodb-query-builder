"""
Unit tests for AggregateBuilder
"""

import pytest

from mongodb_query_builder import AggregateBuilder, QueryFilter
from mongodb_query_builder.exceptions import AggregateBuilderError


class TestAggregateBuilderBasics:
    """Test basic AggregateBuilder functionality"""
    
    def test_empty_pipeline(self, empty_aggregate_builder):
        """Test empty pipeline builds to empty list"""
        result = empty_aggregate_builder.build()
        assert result == []
        assert len(empty_aggregate_builder) == 0
    
    def test_pipeline_length(self, simple_aggregate_builder):
        """Test pipeline length tracking"""
        assert len(simple_aggregate_builder) == 3  # match, group, sort
    
    def test_representation(self, simple_aggregate_builder):
        """Test AggregateBuilder string representation"""
        repr_str = repr(simple_aggregate_builder)
        assert "AggregateBuilder" in repr_str
        assert "stages=" in repr_str
    
    def test_clear_pipeline(self):
        """Test clearing pipeline"""
        builder = AggregateBuilder().match({"status": "active"}).limit(10)
        assert len(builder) == 2
        builder.clear()
        assert len(builder) == 0


class TestAggregateMatch:
    """Test $match stage"""
    
    def test_match_with_query_filter(self):
        """Test match with QueryFilter"""
        query = QueryFilter().field("status").equals("active")
        builder = AggregateBuilder().match(query)
        result = builder.build()
        assert result[0] == {"$match": {"status": "active"}}
    
    def test_match_with_dict(self):
        """Test match with raw dictionary"""
        builder = AggregateBuilder().match({"age": {"$gt": 18}})
        result = builder.build()
        assert result[0] == {"$match": {"age": {"$gt": 18}}}
    
    def test_match_chaining(self):
        """Test multiple match stages"""
        builder = (
            AggregateBuilder()
            .match({"status": "active"})
            .match({"age": {"$gte": 18}})
        )
        result = builder.build()
        assert len(result) == 2
        assert all(stage.get("$match") for stage in result)


class TestAggregateProject:
    """Test $project stage"""
    
    def test_project_include(self):
        """Test project to include fields"""
        builder = AggregateBuilder().project(name=1, email=1, age=1)
        result = builder.build()
        assert result[0] == {"$project": {"name": 1, "email": 1, "age": 1}}
    
    def test_project_exclude(self):
        """Test project to exclude fields"""
        builder = AggregateBuilder().project(password=0, ssn=0)
        result = builder.build()
        assert result[0] == {"$project": {"password": 0, "ssn": 0}}
    
    def test_project_computed(self):
        """Test project with computed fields"""
        builder = AggregateBuilder().project(
            total={"$sum": ["$price", "$tax"]},
            name=1
        )
        result = builder.build()
        assert "$sum" in result[0]["$project"]["total"]
    
    def test_project_empty_raises_error(self):
        """Test project with no fields raises error"""
        with pytest.raises(AggregateBuilderError, match="at least one field"):
            AggregateBuilder().project().build()


class TestAggregateGroup:
    """Test $group stage"""
    
    def test_group_by_field(self):
        """Test group by single field"""
        builder = AggregateBuilder().group(by="$category", count={"$sum": 1})
        result = builder.build()
        assert result[0]["$group"]["_id"] == "$category"
        assert result[0]["$group"]["count"] == {"$sum": 1}
    
    def test_group_by_expression(self):
        """Test group by expression"""
        builder = AggregateBuilder().group(
            by={"year": {"$year": "$date"}},
            total={"$sum": "$amount"}
        )
        result = builder.build()
        assert result[0]["$group"]["_id"]["year"]["$year"] == "$date"
    
    def test_group_all_documents(self):
        """Test group all documents (no _id)"""
        builder = AggregateBuilder().group(by=None, total={"$sum": "$amount"})
        result = builder.build()
        assert result[0]["$group"]["_id"] is None
    
    def test_group_multiple_accumulators(self):
        """Test group with multiple accumulators"""
        builder = AggregateBuilder().group(
            by="$category",
            count={"$sum": 1},
            avg_price={"$avg": "$price"},
            max_price={"$max": "$price"},
            min_price={"$min": "$price"}
        )
        result = builder.build()
        group_stage = result[0]["$group"]
        assert len(group_stage) == 5  # _id + 4 accumulators
    
    def test_group_no_accumulators_raises_error(self):
        """Test group without accumulators raises error"""
        with pytest.raises(AggregateBuilderError, match="at least one accumulator"):
            AggregateBuilder().group(by="$category").build()


class TestAggregateSort:
    """Test $sort stage"""
    
    def test_sort_single_field_ascending(self):
        """Test sort by single field ascending"""
        builder = AggregateBuilder().sort("age", ascending=True)
        result = builder.build()
        assert result[0] == {"$sort": {"age": 1}}
    
    def test_sort_single_field_descending(self):
        """Test sort by single field descending"""
        builder = AggregateBuilder().sort("age", ascending=False)
        result = builder.build()
        assert result[0] == {"$sort": {"age": -1}}
    
    def test_sort_multiple_fields(self):
        """Test sort by multiple fields"""
        builder = AggregateBuilder().sort({"age": 1, "name": -1})
        result = builder.build()
        assert result[0] == {"$sort": {"age": 1, "name": -1}}


class TestAggregateLimitSkip:
    """Test $limit and $skip stages"""
    
    def test_limit(self):
        """Test limit stage"""
        builder = AggregateBuilder().limit(10)
        result = builder.build()
        assert result[0] == {"$limit": 10}
    
    def test_limit_zero_raises_error(self):
        """Test limit with zero raises error"""
        with pytest.raises(AggregateBuilderError, match="limit count must be positive"):
            AggregateBuilder().limit(0).build()
    
    def test_limit_negative_raises_error(self):
        """Test limit with negative value raises error"""
        with pytest.raises(AggregateBuilderError, match="limit count must be positive"):
            AggregateBuilder().limit(-1).build()
    
    def test_skip(self):
        """Test skip stage"""
        builder = AggregateBuilder().skip(20)
        result = builder.build()
        assert result[0] == {"$skip": 20}
    
    def test_skip_negative_raises_error(self):
        """Test skip with negative value raises error"""
        with pytest.raises(AggregateBuilderError, match="non-negative"):
            AggregateBuilder().skip(-1).build()
    
    def test_pagination_pattern(self):
        """Test typical pagination pattern"""
        builder = AggregateBuilder().skip(20).limit(10)
        result = builder.build()
        assert result[0]["$skip"] == 20
        assert result[1]["$limit"] == 10


class TestAggregateUnwind:
    """Test $unwind stage"""
    
    def test_unwind_simple(self):
        """Test simple unwind"""
        builder = AggregateBuilder().unwind("tags")
        result = builder.build()
        assert result[0] == {"$unwind": "$tags"}
    
    def test_unwind_with_dollar(self):
        """Test unwind with $ prefix already present"""
        builder = AggregateBuilder().unwind("$tags")
        result = builder.build()
        assert result[0] == {"$unwind": "$tags"}
    
    def test_unwind_preserve_null(self):
        """Test unwind with preserve null"""
        builder = AggregateBuilder().unwind("tags", preserve_null=True)
        result = builder.build()
        assert result[0]["$unwind"]["path"] == "$tags"
        assert result[0]["$unwind"]["preserveNullAndEmptyArrays"] is True
    
    def test_unwind_with_index(self):
        """Test unwind with array index"""
        builder = AggregateBuilder().unwind(
            "items",
            include_array_index="item_index"
        )
        result = builder.build()
        assert result[0]["$unwind"]["includeArrayIndex"] == "item_index"
    
    def test_unwind_empty_path_raises_error(self):
        """Test unwind with empty path raises error"""
        with pytest.raises(AggregateBuilderError, match="cannot be empty"):
            AggregateBuilder().unwind("").build()


class TestAggregateLookup:
    """Test $lookup stage"""
    
    def test_lookup_simple(self):
        """Test simple lookup"""
        builder = AggregateBuilder().lookup(
            "orders",
            "_id",
            "user_id",
            "user_orders"
        )
        result = builder.build()
        lookup = result[0]["$lookup"]
        assert lookup["from"] == "orders"
        assert lookup["localField"] == "_id"
        assert lookup["foreignField"] == "user_id"
        assert lookup["as"] == "user_orders"
    
    def test_lookup_missing_params_raises_error(self):
        """Test lookup with missing parameters raises error"""
        with pytest.raises(AggregateBuilderError):
            AggregateBuilder().lookup("", "_id", "user_id", "orders").build()
    
    def test_lookup_pipeline(self):
        """Test lookup with pipeline"""
        builder = AggregateBuilder().lookup_pipeline(
            "orders",
            {"user_id": "$_id"},
            [{"$match": {"$expr": {"$eq": ["$user_id", "$$user_id"]}}}],
            "user_orders"
        )
        result = builder.build()
        lookup = result[0]["$lookup"]
        assert "pipeline" in lookup
        assert "let" in lookup
        assert lookup["let"]["user_id"] == "$_id"


class TestAggregateAddFields:
    """Test $addFields and $set stages"""
    
    def test_add_fields(self):
        """Test add fields stage"""
        builder = AggregateBuilder().add_fields(
            total={"$sum": ["$price", "$tax"]},
            discounted_price={"$multiply": ["$price", 0.9]}
        )
        result = builder.build()
        assert "$addFields" in result[0]
        assert len(result[0]["$addFields"]) == 2
    
    def test_add_fields_empty_raises_error(self):
        """Test add fields with no fields raises error"""
        with pytest.raises(AggregateBuilderError, match="at least one field"):
            AggregateBuilder().add_fields().build()
    
    def test_set_stage(self):
        """Test set stage (alias for addFields)"""
        builder = AggregateBuilder().set(status="active")
        result = builder.build()
        assert "$set" in result[0]
    
    def test_set_empty_raises_error(self):
        """Test set with no fields raises error"""
        with pytest.raises(AggregateBuilderError, match="at least one field"):
            AggregateBuilder().set().build()


class TestAggregateUnset:
    """Test $unset stage"""
    
    def test_unset_single_field(self):
        """Test unset single field"""
        builder = AggregateBuilder().unset("password")
        result = builder.build()
        assert result[0] == {"$unset": ["password"]}
    
    def test_unset_multiple_fields(self):
        """Test unset multiple fields"""
        builder = AggregateBuilder().unset("password", "ssn", "credit_card")
        result = builder.build()
        assert result[0] == {"$unset": ["password", "ssn", "credit_card"]}
    
    def test_unset_no_fields_raises_error(self):
        """Test unset with no fields raises error"""
        with pytest.raises(AggregateBuilderError, match="at least one field"):
            AggregateBuilder().unset().build()


class TestAggregateReplaceRoot:
    """Test $replaceRoot and $replaceWith stages"""
    
    def test_replace_root_with_string(self):
        """Test replace root with field name"""
        builder = AggregateBuilder().replace_root("embedded_doc")
        result = builder.build()
        assert result[0]["$replaceRoot"]["newRoot"] == "$embedded_doc"
    
    def test_replace_root_with_dollar(self):
        """Test replace root with $ prefix"""
        builder = AggregateBuilder().replace_root("$embedded_doc")
        result = builder.build()
        assert result[0]["$replaceRoot"]["newRoot"] == "$embedded_doc"
    
    def test_replace_root_with_expression(self):
        """Test replace root with expression"""
        builder = AggregateBuilder().replace_root(
            {"$mergeObjects": ["$doc1", "$doc2"]}
        )
        result = builder.build()
        assert "$mergeObjects" in result[0]["$replaceRoot"]["newRoot"]
    
    def test_replace_with(self):
        """Test replace with (alias)"""
        builder = AggregateBuilder().replace_with("$embedded")
        result = builder.build()
        assert "$replaceWith" in result[0]


class TestAggregateFacet:
    """Test $facet stage"""
    
    def test_facet_multiple_pipelines(self):
        """Test facet with multiple pipelines"""
        builder = AggregateBuilder().facet(
            by_category=[{"$group": {"_id": "$category", "count": {"$sum": 1}}}],
            by_status=[{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
        )
        result = builder.build()
        facet = result[0]["$facet"]
        assert "by_category" in facet
        assert "by_status" in facet
    
    def test_facet_empty_raises_error(self):
        """Test facet with no facets raises error"""
        with pytest.raises(AggregateBuilderError, match="at least one facet"):
            AggregateBuilder().facet().build()


class TestAggregateBucket:
    """Test $bucket and $bucketAuto stages"""
    
    def test_bucket(self):
        """Test bucket stage"""
        builder = AggregateBuilder().bucket(
            group_by="$age",
            boundaries=[0, 18, 30, 50, 100],
            output={"count": {"$sum": 1}}
        )
        result = builder.build()
        bucket = result[0]["$bucket"]
        assert bucket["groupBy"] == "$age"
        assert len(bucket["boundaries"]) == 5
        assert "output" in bucket
    
    def test_bucket_with_default(self):
        """Test bucket with default bucket"""
        builder = AggregateBuilder().bucket(
            group_by="$age",
            boundaries=[0, 18, 65],
            default="Other"
        )
        result = builder.build()
        assert result[0]["$bucket"]["default"] == "Other"
    
    def test_bucket_missing_boundaries_raises_error(self):
        """Test bucket without boundaries raises error"""
        with pytest.raises(AggregateBuilderError, match="at least 2 boundaries"):
            AggregateBuilder().bucket(
                group_by="$age",
                boundaries=[0]
            ).build()
    
    def test_bucket_auto(self):
        """Test bucketAuto stage"""
        builder = AggregateBuilder().bucket_auto(
            group_by="$price",
            buckets=5,
            output={"count": {"$sum": 1}}
        )
        result = builder.build()
        bucket_auto = result[0]["$bucketAuto"]
        assert bucket_auto["groupBy"] == "$price"
        assert bucket_auto["buckets"] == 5
    
    def test_bucket_auto_zero_buckets_raises_error(self):
        """Test bucketAuto with zero buckets raises error"""
        with pytest.raises(AggregateBuilderError, match="must be positive"):
            AggregateBuilder().bucket_auto(
                group_by="$price",
                buckets=0
            ).build()


class TestAggregateSample:
    """Test $sample stage"""
    
    def test_sample(self):
        """Test sample stage"""
        builder = AggregateBuilder().sample(10)
        result = builder.build()
        assert result[0] == {"$sample": {"size": 10}}
    
    def test_sample_zero_raises_error(self):
        """Test sample with zero raises error"""
        with pytest.raises(AggregateBuilderError, match="must be positive"):
            AggregateBuilder().sample(0).build()


class TestAggregateCount:
    """Test $count and $sortByCount stages"""
    
    def test_count(self):
        """Test count stage"""
        builder = AggregateBuilder().count("total")
        result = builder.build()
        assert result[0] == {"$count": "total"}
    
    def test_count_default_name(self):
        """Test count with default field name"""
        builder = AggregateBuilder().count()
        result = builder.build()
        assert result[0] == {"$count": "count"}
    
    def test_count_empty_name_raises_error(self):
        """Test count with empty name raises error"""
        with pytest.raises(AggregateBuilderError, match="cannot be empty"):
            AggregateBuilder().count("").build()
    
    def test_sort_by_count(self):
        """Test sortByCount stage"""
        builder = AggregateBuilder().sort_by_count("$category")
        result = builder.build()
        assert result[0] == {"$sortByCount": "$category"}
    
    def test_sort_by_count_adds_dollar(self):
        """Test sortByCount adds $ prefix"""
        builder = AggregateBuilder().sort_by_count("category")
        result = builder.build()
        assert result[0]["$sortByCount"] == "$category"


class TestAggregateGraphLookup:
    """Test $graphLookup stage"""
    
    def test_graph_lookup(self):
        """Test graph lookup stage"""
        builder = AggregateBuilder().graph_lookup(
            from_collection="employees",
            start_with="$reports_to",
            connect_from_field="reports_to",
            connect_to_field="_id",
            as_field="reporting_hierarchy"
        )
        result = builder.build()
        graph = result[0]["$graphLookup"]
        assert graph["from"] == "employees"
        assert graph["startWith"] == "$reports_to"
        assert graph["as"] == "reporting_hierarchy"
    
    def test_graph_lookup_with_max_depth(self):
        """Test graph lookup with max depth"""
        builder = AggregateBuilder().graph_lookup(
            from_collection="employees",
            start_with="$manager_id",
            connect_from_field="manager_id",
            connect_to_field="_id",
            as_field="hierarchy",
            max_depth=3
        )
        result = builder.build()
        assert result[0]["$graphLookup"]["maxDepth"] == 3


class TestAggregateUnionWith:
    """Test $unionWith stage"""
    
    def test_union_with_collection(self):
        """Test union with another collection"""
        builder = AggregateBuilder().union_with("archive_collection")
        result = builder.build()
        assert result[0] == {"$unionWith": "archive_collection"}
    
    def test_union_with_pipeline(self):
        """Test union with pipeline"""
        builder = AggregateBuilder().union_with(
            "archive_collection",
            pipeline=[{"$match": {"year": 2023}}]
        )
        result = builder.build()
        union = result[0]["$unionWith"]
        assert union["coll"] == "archive_collection"
        assert "pipeline" in union


class TestAggregateOutMerge:
    """Test $out and $merge stages"""
    
    def test_out_simple(self):
        """Test out stage"""
        builder = AggregateBuilder().out("result_collection")
        result = builder.build()
        assert result[0] == {"$out": "result_collection"}
    
    def test_out_with_db(self):
        """Test out with database"""
        builder = AggregateBuilder().out("result_collection", db="other_db")
        result = builder.build()
        out = result[0]["$out"]
        assert out["db"] == "other_db"
        assert out["coll"] == "result_collection"
    
    def test_merge(self):
        """Test merge stage"""
        builder = AggregateBuilder().merge(
            "target_collection",
            on="_id",
            when_matched="replace"
        )
        result = builder.build()
        merge = result[0]["$merge"]
        assert merge["into"] == "target_collection"
        assert merge["on"] == "_id"
        assert merge["whenMatched"] == "replace"


class TestAggregateCustomStage:
    """Test custom stage"""
    
    def test_custom_stage(self):
        """Test adding custom stage"""
        custom = {"$customOperator": {"field": "value"}}
        builder = AggregateBuilder().custom_stage(custom)
        result = builder.build()
        assert result[0] == custom
    
    def test_custom_stage_empty_raises_error(self):
        """Test custom stage with empty dict raises error"""
        with pytest.raises(AggregateBuilderError, match="requires a stage"):
            AggregateBuilder().custom_stage({}).build()


class TestAggregateComplexPipelines:
    """Test complex aggregation pipelines"""
    
    def test_full_analytics_pipeline(self):
        """Test complete analytics pipeline"""
        builder = (
            AggregateBuilder()
            .match(QueryFilter().field("status").equals("completed"))
            .lookup("users", "user_id", "_id", "user")
            .unwind("user")
            .group(
                by="$user.country",
                total_orders={"$sum": 1},
                total_revenue={"$sum": "$amount"}
            )
            .sort("total_revenue", ascending=False)
            .limit(10)
        )
        result = builder.build()
        assert len(result) == 6
        assert result[0]["$match"]
        assert result[1]["$lookup"]
        assert result[2]["$unwind"]
        assert result[3]["$group"]
        assert result[4]["$sort"]
        assert result[5]["$limit"]
    
    def test_faceted_aggregation(self):
        """Test faceted aggregation"""
        builder = (
            AggregateBuilder()
            .match({"status": "active"})
            .facet(
                by_category=[
                    {"$group": {"_id": "$category", "count": {"$sum": 1}}}
                ],
                price_ranges=[
                    {"$bucket": {
                        "groupBy": "$price",
                        "boundaries": [0, 50, 100, 200]
                    }}
                ]
            )
        )
        result = builder.build()
        assert len(result) == 2
        assert "$facet" in result[1]