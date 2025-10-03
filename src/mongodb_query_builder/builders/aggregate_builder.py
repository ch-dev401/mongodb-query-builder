"""
MongoDB Aggregation Pipeline Builder

Provides a fluent interface for building MongoDB aggregation pipelines with
comprehensive support for all aggregation stages.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..exceptions import AggregateBuilderError, ValidationError
from ..operators import AggregateOperator
from ..utils import ensure_dollar_prefix, validate_positive_number, validate_string_not_empty
from .query_filter import QueryFilter


class AggregateBuilder:
    """
    MongoDB Aggregation Pipeline Builder
    
    This class provides a chainable interface for building MongoDB aggregation
    pipelines with support for all standard aggregation stages.
    
    Examples:
        # Simple aggregation
        >>> pipeline = AggregateBuilder()\\
        ...     .match(QueryFilter().field("status").equals("active"))\\
        ...     .group(by="_id", count={"$sum": 1})\\
        ...     .sort("count", ascending=False)\\
        ...     .build()
        
        # Complex aggregation with lookup
        >>> pipeline = AggregateBuilder()\\
        ...     .match(QueryFilter().field("age").greater_than(18))\\
        ...     .lookup("orders", "_id", "user_id", "user_orders")\\
        ...     .unwind("user_orders")\\
        ...     .group(by="$_id", total_orders={"$sum": "$user_orders.amount"})\\
        ...     .build()
    """

    def __init__(self):
        """Initialize a new AggregateBuilder"""
        self._pipeline: List[Dict[str, Any]] = []

    def match(self, filter_obj: Union[QueryFilter, Dict[str, Any]]) -> "AggregateBuilder":
        """
        Add $match stage to filter documents

        Args:
            filter_obj: QueryFilter object or raw filter dictionary

        Returns:
            Self for chaining
        """
        if isinstance(filter_obj, QueryFilter):
            filter_dict = filter_obj.build()
        else:
            filter_dict = filter_obj

        self._pipeline.append({AggregateOperator.MATCH: filter_dict})
        return self

    def project(self, **fields) -> "AggregateBuilder":
        """
        Add $project stage to include/exclude/compute fields

        Args:
            **fields: Field specifications

        Returns:
            Self for chaining

        Examples:
            >>> .project(name=1, email=1, age=1)  # Include fields
            >>> .project(password=0)  # Exclude field
            >>> .project(total={"$sum": ["$price", "$tax"]})  # Computed field
        """
        if not fields:
            raise AggregateBuilderError("project() requires at least one field")

        self._pipeline.append({AggregateOperator.PROJECT: fields})
        return self

    def group(
        self, by: Union[str, Dict[str, Any], None] = None, **accumulators
    ) -> "AggregateBuilder":
        """
        Add $group stage to group documents and compute aggregates

        Args:
            by: Field(s) to group by (None for grouping all documents)
            **accumulators: Accumulator expressions

        Returns:
            Self for chaining

        Examples:
            >>> .group(by="$category", count={"$sum": 1})
            >>> .group(by={"year": {"$year": "$date"}}, total={"$sum": "$amount"})
            >>> .group(by=None, total={"$sum": "$amount"})  # Group all documents
        """
        if not accumulators:
            raise AggregateBuilderError("group() requires at least one accumulator")

        group_stage = {"_id": by}
        group_stage.update(accumulators)
        self._pipeline.append({AggregateOperator.GROUP: group_stage})
        return self

    def sort(self, field: Union[str, Dict[str, int]], ascending: bool = True) -> "AggregateBuilder":
        """
        Add $sort stage to order documents

        Args:
            field: Field name or sort specification
            ascending: Sort direction (only used if field is a string)

        Returns:
            Self for chaining

        Examples:
            >>> .sort("age")  # Sort by age ascending
            >>> .sort("age", ascending=False)  # Sort descending
            >>> .sort({"age": 1, "name": -1})  # Multiple fields
        """
        if isinstance(field, str):
            sort_dict = {field: 1 if ascending else -1}
        else:
            sort_dict = field

        self._pipeline.append({AggregateOperator.SORT: sort_dict})
        return self

    def limit(self, count: int) -> "AggregateBuilder":
        """
        Add $limit stage to limit number of documents

        Args:
            count: Maximum number of documents to return

        Returns:
            Self for chaining
        """
        try:
            validate_positive_number(count, "limit count")

        except ValidationError as e:
            raise AggregateBuilderError(e)

        self._pipeline.append({AggregateOperator.LIMIT: count})
        return self

    def skip(self, count: int) -> "AggregateBuilder":
        """
        Add $skip stage to skip documents

        Args:
            count: Number of documents to skip

        Returns:
            Self for chaining
        """
        try:

            validate_positive_number(count, "skip count", allow_zero=True)
        except ValidationError as e:
            raise AggregateBuilderError(e)

        self._pipeline.append({AggregateOperator.SKIP: count})
        return self

    def unwind(
        self, path: str, preserve_null: bool = False, include_array_index: Optional[str] = None
    ) -> "AggregateBuilder":
        """
        Add $unwind stage to deconstruct array fields

        Args:
            path: Array field path to unwind
            preserve_null: Keep documents with null/empty arrays
            include_array_index: Field name to store array index

        Returns:
            Self for chaining

        Examples:
            >>> .unwind("tags")  # Simple unwind
            >>> .unwind("tags", preserve_null=True)  # Keep null/empty arrays
            >>> .unwind("items", include_array_index="item_index")
        """

        try:
            validate_string_not_empty(path, "unwind path")

            # Ensure path starts with $
            path = ensure_dollar_prefix(path)

        except ValidationError as e:
            raise AggregateBuilderError(e)

        if preserve_null or include_array_index:
            unwind_config: Dict[str, Any] = {"path": path}
            if preserve_null:
                unwind_config["preserveNullAndEmptyArrays"] = True
            if include_array_index:
                unwind_config["includeArrayIndex"] = include_array_index
        else:
            unwind_config = path

        self._pipeline.append({AggregateOperator.UNWIND: unwind_config})
        return self

    def lookup(
        self, from_collection: str, local_field: str, foreign_field: str, as_field: str
    ) -> "AggregateBuilder":
        """
        Add $lookup stage to perform left outer join

        Args:
            from_collection: Collection to join with
            local_field: Field from input documents
            foreign_field: Field from documents of the from collection
            as_field: Output array field name

        Returns:
            Self for chaining

        Example:
            >>> .lookup("orders", "_id", "user_id", "user_orders")
        """
        if not all([from_collection, local_field, foreign_field, as_field]):
            raise AggregateBuilderError(
                "lookup() requires from_collection, local_field, foreign_field, and as_field"
            )

        lookup_config = {
            "from": from_collection,
            "localField": local_field,
            "foreignField": foreign_field,
            "as": as_field,
        }
        self._pipeline.append({AggregateOperator.LOOKUP: lookup_config})
        return self

    def lookup_pipeline(
        self, from_collection: str, let_vars: Dict[str, str], pipeline: List[Dict], as_field: str
    ) -> "AggregateBuilder":
        """
        Add $lookup with pipeline (advanced join with complex conditions)

        Args:
            from_collection: Collection to join with
            let_vars: Variables to use in the pipeline
            pipeline: Aggregation pipeline to run on joined collection
            as_field: Output array field name

        Returns:
            Self for chaining

        Example:
            >>> .lookup_pipeline(
            ...     "orders",
            ...     {"user_id": "$_id"},
            ...     [{"$match": {"$expr": {"$eq": ["$user_id", "$$user_id"]}}}],
            ...     "user_orders"
            ... )
        """
        if not all([from_collection, as_field]):
            raise AggregateBuilderError("lookup_pipeline() requires from_collection and as_field")

        lookup_config = {
            "from": from_collection,
            "let": let_vars or {},
            "pipeline": pipeline or [],
            "as": as_field,
        }
        self._pipeline.append({AggregateOperator.LOOKUP: lookup_config})
        return self

    def add_fields(self, **fields) -> "AggregateBuilder":
        """
        Add $addFields stage to add new computed fields

        Args:
            **fields: Field specifications

        Returns:
            Self for chaining

        Example:
            >>> .add_fields(total={"$sum": ["$price", "$tax"]})
        """
        if not fields:
            raise AggregateBuilderError("add_fields() requires at least one field")

        self._pipeline.append({AggregateOperator.ADD_FIELDS: fields})
        return self

    def set(self, **fields) -> "AggregateBuilder":
        """
        Add $set stage (alias for $addFields)

        Args:
            **fields: Field specifications

        Returns:
            Self for chaining
        """
        if not fields:
            raise AggregateBuilderError("set() requires at least one field")

        self._pipeline.append({AggregateOperator.SET: fields})
        return self

    def unset(self, *fields: str) -> "AggregateBuilder":
        """
        Add $unset stage to remove fields

        Args:
            *fields: Field names to remove

        Returns:
            Self for chaining

        Example:
            >>> .unset("password", "ssn")
        """
        if not fields:
            raise AggregateBuilderError("unset() requires at least one field")

        self._pipeline.append({AggregateOperator.UNSET: list(fields)})
        return self

    def replace_root(self, new_root: Union[str, Dict[str, Any]]) -> "AggregateBuilder":
        """
        Add $replaceRoot stage to replace root document

        Args:
            new_root: New root specification

        Returns:
            Self for chaining

        Example:
            >>> .replace_root("$embedded_doc")
            >>> .replace_root({"$mergeObjects": ["$doc1", "$doc2"]})
        """
        if isinstance(new_root, str):
            try:
                new_root = ensure_dollar_prefix(new_root)

            except ValidationError as e:
                raise AggregateBuilderError(e)

            new_root_config = {"newRoot": new_root}
        else:
            new_root_config = {"newRoot": new_root}

        self._pipeline.append({AggregateOperator.REPLACE_ROOT: new_root_config})
        return self

    def replace_with(self, replacement: Union[str, Dict[str, Any]]) -> "AggregateBuilder":
        """
        Add $replaceWith stage (alias for $replaceRoot in MongoDB 4.2+)

        Args:
            replacement: Replacement specification

        Returns:
            Self for chaining
        """
        if isinstance(replacement, str):
            try:
                replacement = ensure_dollar_prefix(replacement)

            except ValidationError as e:
                raise AggregateBuilderError(e)

        self._pipeline.append({AggregateOperator.REPLACE_WITH: replacement})
        return self

    def facet(self, **facets: List[Dict[str, Any]]) -> "AggregateBuilder":
        """
        Add $facet stage for multiple aggregation pipelines

        Args:
            **facets: Named pipelines

        Returns:
            Self for chaining

        Example:
            >>> .facet(
            ...     by_category=[{"$group": {"_id": "$category", "count": {"$sum": 1}}}],
            ...     by_status=[{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
            ... )
        """
        if not facets:
            raise AggregateBuilderError("facet() requires at least one facet")

        self._pipeline.append({AggregateOperator.FACET: facets})
        return self

    def bucket(
        self,
        group_by: str,
        boundaries: List[Union[int, float, datetime]],
        default: Any = None,
        output: Optional[Dict[str, Any]] = None,
    ) -> "AggregateBuilder":
        """
        Add $bucket stage to categorize documents into buckets

        Args:
            group_by: Expression to group by
            boundaries: Array of bucket boundaries
            default: Default bucket for values outside boundaries
            output: Output document specification

        Returns:
            Self for chaining

        Example:
            >>> .bucket(
            ...     group_by="$age",
            ...     boundaries=[0, 18, 30, 50, 100],
            ...     default="Other",
            ...     output={"count": {"$sum": 1}, "avg_income": {"$avg": "$income"}}
            ... )
        """
        if not group_by:
            raise AggregateBuilderError("bucket() requires group_by")
        if not boundaries or len(boundaries) < 2:
            raise AggregateBuilderError("bucket() requires at least 2 boundaries")

        try:
            group_by = ensure_dollar_prefix(group_by)

        except ValidationError as e:
            raise AggregateBuilderError(e)

        bucket_config = {"groupBy": group_by, "boundaries": boundaries}
        if default is not None:
            bucket_config["default"] = default
        if output:
            bucket_config["output"] = output

        self._pipeline.append({AggregateOperator.BUCKET: bucket_config})
        return self

    def bucket_auto(
        self,
        group_by: str,
        buckets: int,
        output: Optional[Dict[str, Any]] = None,
        granularity: Optional[str] = None,
    ) -> "AggregateBuilder":
        """
        Add $bucketAuto stage for automatic bucketing

        Args:
            group_by: Expression to group by
            buckets: Number of buckets
            output: Output document specification
            granularity: Granularity for bucket boundaries

        Returns:
            Self for chaining

        Example:
            >>> .bucket_auto(
            ...     group_by="$price",
            ...     buckets=5,
            ...     output={"count": {"$sum": 1}, "avg_rating": {"$avg": "$rating"}}
            ... )
        """
        try:

            validate_string_not_empty(group_by, "bucket_auto group_by")
            validate_positive_number(buckets, "bucket_auto buckets")

            group_by = ensure_dollar_prefix(group_by)

        except ValidationError as e:
            raise AggregateBuilderError(e)

        bucket_config = {"groupBy": group_by, "buckets": buckets}
        if output:
            bucket_config["output"] = output
        if granularity:
            bucket_config["granularity"] = granularity

        self._pipeline.append({AggregateOperator.BUCKET_AUTO: bucket_config})
        return self

    def sample(self, size: int) -> "AggregateBuilder":
        """
        Add $sample stage for random document sampling

        Args:
            size: Number of documents to sample

        Returns:
            Self for chaining
        """
        try:
            validate_positive_number(size, "sample size")

        except ValidationError as e:
            raise AggregateBuilderError(e)

        self._pipeline.append({AggregateOperator.SAMPLE: {"size": size}})
        return self

    def count(self, field_name: str = "count") -> "AggregateBuilder":
        """
        Add $count stage to count documents

        Args:
            field_name: Name of the output field

        Returns:
            Self for chaining
        """
        try:
            validate_string_not_empty(field_name, "count field_name")

        except ValidationError as e:
            raise AggregateBuilderError(e)

        self._pipeline.append({AggregateOperator.COUNT: field_name})
        return self

    def sort_by_count(self, expression: str) -> "AggregateBuilder":
        """
        Add $sortByCount stage to group and count, then sort by count

        Args:
            expression: Expression to group by

        Returns:
            Self for chaining

        Example:
            >>> .sort_by_count("$category")
        """
        try:
            validate_string_not_empty(expression, "sort_by_count expression")

            expression = ensure_dollar_prefix(expression)

        except ValidationError as e:
            raise AggregateBuilderError(e)

        self._pipeline.append({AggregateOperator.SORT_BY_COUNT: expression})
        return self

    def graph_lookup(
        self,
        from_collection: str,
        start_with: str,
        connect_from_field: str,
        connect_to_field: str,
        as_field: str,
        max_depth: Optional[int] = None,
        depth_field: Optional[str] = None,
        restrict_search_with_match: Optional[Dict[str, Any]] = None,
    ) -> "AggregateBuilder":
        """
        Add $graphLookup stage for recursive graph traversal

        Args:
            from_collection: Collection to perform lookup on
            start_with: Expression for starting documents
            connect_from_field: Field to recursively match against
            connect_to_field: Field to match connect_from_field to
            as_field: Output array field name
            max_depth: Maximum recursion depth
            depth_field: Field name for recursion depth
            restrict_search_with_match: Additional match conditions

        Returns:
            Self for chaining
        """
        if not all([from_collection, start_with, connect_from_field, connect_to_field, as_field]):
            raise AggregateBuilderError(
                "graph_lookup() requires from_collection, start_with, "
                "connect_from_field, connect_to_field, and as_field"
            )

        try:
            graph_config = {
                "from": from_collection,
                "startWith": ensure_dollar_prefix(start_with),
                "connectFromField": connect_from_field,
                "connectToField": connect_to_field,
                "as": as_field,
            }

        except ValidationError as e:
            raise AggregateBuilderError(e)

        if max_depth is not None:
            graph_config["maxDepth"] = max_depth
        if depth_field:
            graph_config["depthField"] = depth_field
        if restrict_search_with_match:
            graph_config["restrictSearchWithMatch"] = restrict_search_with_match

        self._pipeline.append({AggregateOperator.GRAPH_LOOKUP: graph_config})
        return self

    def union_with(
        self, collection: str, pipeline: Optional[List[Dict[str, Any]]] = None
    ) -> "AggregateBuilder":
        """
        Add $unionWith stage to combine with another collection

        Args:
            collection: Collection to union with
            pipeline: Optional pipeline to apply to the collection

        Returns:
            Self for chaining
        """
        try:
            validate_string_not_empty(collection, "union_with collection")

            union_config: Union[str, Dict[str, Any]]
            if pipeline:
                union_config = {"coll": collection, "pipeline": pipeline}
            else:
                union_config = collection

            self._pipeline.append({AggregateOperator.UNION_WITH: union_config})
            return self
        except ValidationError as e:
            raise AggregateBuilderError(e)

    def out(self, collection: str, db: Optional[str] = None) -> "AggregateBuilder":
        """
        Add $out stage to write results to a collection

        Args:
            collection: Target collection name
            db: Optional target database name

        Returns:
            Self for chaining
        """
        try:
            validate_string_not_empty(collection, "out collection")

            if db:
                out_config = {"db": db, "coll": collection}
            else:
                out_config = collection

            self._pipeline.append({AggregateOperator.OUT: out_config})
            return self

        except ValidationError as e:
            raise AggregateBuilderError(e)

    def merge(
        self,
        into: Union[str, Dict[str, str]],
        on: Optional[Union[str, List[str]]] = None,
        let_vars: Optional[Dict[str, Any]] = None,
        when_matched: str = "merge",
        when_not_matched: str = "insert",
    ) -> "AggregateBuilder":
        """
        Add $merge stage to write results to a collection

        Args:
            into: Target collection (string or {db, coll})
            on: Field(s) to match on
            let_vars: Variables for whenMatched pipeline
            when_matched: Action when documents match
            when_not_matched: Action when documents don't match

        Returns:
            Self for chaining

        Example:
            >>> .merge("target_collection", on="_id", when_matched="replace")
        """
        if not into:
            raise AggregateBuilderError("merge() requires into")

        merge_config: Dict[str, Any] = {"into": into}

        if on:
            merge_config["on"] = on
        if let_vars:
            merge_config["let"] = let_vars
        merge_config["whenMatched"] = when_matched
        merge_config["whenNotMatched"] = when_not_matched

        self._pipeline.append({AggregateOperator.MERGE: merge_config})
        return self

    def redact(self, expression: Dict[str, Any]) -> "AggregateBuilder":
        """
        Add $redact stage to restrict document content

        Args:
            expression: Redaction expression

        Returns:
            Self for chaining
        """
        if not expression:
            raise AggregateBuilderError("redact() requires an expression")

        self._pipeline.append({AggregateOperator.REDACT: expression})
        return self

    def custom_stage(self, stage: Dict[str, Any]) -> "AggregateBuilder":
        """
        Add a custom aggregation stage

        Args:
            stage: Raw stage specification

        Returns:
            Self for chaining
        """
        if not stage:
            raise AggregateBuilderError("custom_stage() requires a stage")

        self._pipeline.append(stage)
        return self

    def build(self) -> List[Dict[str, Any]]:
        """
        Build the final aggregation pipeline

        Returns:
            List of aggregation stages
        """
        return self._pipeline

    def clear(self) -> "AggregateBuilder":
        """
        Clear the pipeline

        Returns:
            Self for chaining
        """
        self._pipeline = []
        return self

    def __len__(self) -> int:
        """Return the number of stages in the pipeline"""
        return len(self._pipeline)

    def __repr__(self):
        return f"AggregateBuilder(stages={len(self._pipeline)})"


__all__ = ["AggregateBuilder"]
