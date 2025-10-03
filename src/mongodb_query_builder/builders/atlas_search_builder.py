"""
MongoDB Atlas Search Query Builder

Provides a fluent interface for building MongoDB Atlas Search queries with
support for compound queries, facets, and various search operators.
"""

from typing import Any, Dict, List, Optional, Union

from ..exceptions import AtlasSearchError, ValidationError
from ..operators import AggregateOperator
from ..utils import validate_at_least_one, validate_string_not_empty


class CompoundBuilder:
    """
    MongoDB Atlas Search Compound Query Builder

    Builds compound queries with must, should, mustNot, and filter clauses.

    Examples:
        >>> compound = CompoundBuilder()
        >>> compound.must().text("python", path="skills")
        >>> compound.should().text("senior", path="level", score=2.0)
        >>> compound.filter().range("experience", gte=3)
        >>> search = AtlasSearchBuilder().compound(compound).build()
    """

    def __init__(self):
        """Initialize a new CompoundBuilder"""
        self._clauses = {"must": [], "mustNot": [], "should": [], "filter": []}
        self._minimum_should_match = None

    def must(self) -> "ClauseBuilder":
        """
        Start building a must clause (all conditions must match)

        Returns:
            ClauseBuilder for chaining
        """
        return ClauseBuilder(self._clauses["must"], self)

    def should(self) -> "ClauseBuilder":
        """
        Start building a should clause (at least one should match)

        Returns:
            ClauseBuilder for chaining
        """
        return ClauseBuilder(self._clauses["should"], self)

    def must_not(self) -> "ClauseBuilder":
        """
        Start building a mustNot clause (none must match)

        Returns:
            ClauseBuilder for chaining
        """
        return ClauseBuilder(self._clauses["mustNot"], self)

    def filter(self) -> "ClauseBuilder":
        """
        Start building a filter clause (doesn't affect scoring)

        Returns:
            ClauseBuilder for chaining
        """
        return ClauseBuilder(self._clauses["filter"], self)

    def minimum_should_match(self, value: int) -> "CompoundBuilder":
        """
        Set minimum number of should clauses that must match

        Args:
            value: Minimum number of should clauses

        Returns:
            Self for chaining
        """
        if value < 0:
            raise AtlasSearchError("minimum_should_match must be non-negative")

        self._minimum_should_match = value
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build the compound query

        Returns:
            Dictionary representing the compound query
        """
        compound = {k: v for k, v in self._clauses.items() if v}
        if self._minimum_should_match is not None and "should" in compound:
            compound["minimumShouldMatch"] = self._minimum_should_match
        return compound


class ClauseBuilder:
    """
    Builder for individual clauses within a compound query

    Returns parent CompoundBuilder for better chaining.
    """

    def __init__(self, clause_list: List[Dict[str, Any]], parent: "CompoundBuilder"):
        """
        Initialize a ClauseBuilder

        Args:
            clause_list: List to append clauses to
            parent: Parent CompoundBuilder
        """
        self._clause_list = clause_list
        self._parent = parent

    def text(
        self,
        query: str,
        path: Union[str, List[str]],
        fuzzy: Optional[Dict[str, Any]] = None,
        score: Optional[float] = None,
    ) -> "ClauseBuilder":
        """
        Add a text search clause

        Args:
            query: Search query text
            path: Field path(s) to search
            fuzzy: Fuzzy matching configuration
            score: Score boost value

        Returns:
            Self for chaining
        """
        try:
            validate_string_not_empty(query, "text query")

            if not path:
                raise AtlasSearchError("text() requires a path")

            clause = {"text": {"query": query, "path": path}}
            if fuzzy:
                clause["text"]["fuzzy"] = fuzzy
            if score:
                clause["text"]["score"] = {"boost": {"value": score}}
            self._clause_list.append(clause)
            return self

        except ValidationError as e:
            raise AtlasSearchError(e)

    def phrase(
        self, query: str, path: Union[str, List[str]], slop: int = 0, score: Optional[float] = None
    ) -> "ClauseBuilder":
        """
        Add a phrase search clause

        Args:
            query: Phrase to search for
            path: Field path(s) to search
            slop: Maximum distance between terms
            score: Score boost value

        Returns:
            Self for chaining
        """
        try:
            validate_string_not_empty(query, "phrase query")
            if not path:
                raise AtlasSearchError("phrase() requires a path")

            clause = {"phrase": {"query": query, "path": path, "slop": slop}}
            if score:
                clause["phrase"]["score"] = {"boost": {"value": score}}
            self._clause_list.append(clause)
            return self

        except ValidationError as e:
            raise AtlasSearchError(e)

    def wildcard(
        self,
        query: str,
        path: Union[str, List[str]],
        allow_analyzed_field: bool = False,
        score: Optional[float] = None,
    ) -> "ClauseBuilder":
        """
        Add a wildcard search clause (* and ? supported)

        Args:
            query: Wildcard query
            path: Field path(s) to search
            allow_analyzed_field: Allow searching analyzed fields
            score: Score boost value

        Returns:
            Self for chaining
        """
        validate_string_not_empty(query, "wildcard query")
        if not path:
            raise AtlasSearchError("wildcard() requires a path")

        clause = {
            "wildcard": {"query": query, "path": path, "allowAnalyzedField": allow_analyzed_field}
        }
        if score:
            clause["wildcard"]["score"] = {"boost": {"value": score}}
        self._clause_list.append(clause)
        return self

    def regex(
        self,
        query: str,
        path: Union[str, List[str]],
        allow_analyzed_field: bool = False,
        score: Optional[float] = None,
    ) -> "ClauseBuilder":
        """
        Add a regex search clause

        Args:
            query: Regex pattern
            path: Field path(s) to search
            allow_analyzed_field: Allow searching analyzed fields
            score: Score boost value

        Returns:
            Self for chaining
        """
        validate_string_not_empty(query, "regex query")
        if not path:
            raise AtlasSearchError("regex() requires a path")

        clause = {
            "regex": {"query": query, "path": path, "allowAnalyzedField": allow_analyzed_field}
        }
        if score:
            clause["regex"]["score"] = {"boost": {"value": score}}
        self._clause_list.append(clause)
        return self

    def range(
        self,
        path: str,
        gt: Any = None,
        gte: Any = None,
        lt: Any = None,
        lte: Any = None,
        score: Optional[float] = None,
    ) -> "ClauseBuilder":
        """
        Add a range clause

        Args:
            path: Field path
            gt: Greater than value
            gte: Greater than or equal value
            lt: Less than value
            lte: Less than or equal value
            score: Score boost value

        Returns:
            Self for chaining
        """
        try:
            validate_string_not_empty(path, "range path")
            validate_at_least_one(gt, gte, lt, lte, context="At least one range boundary")

            range_config = {"path": path}
            if gt is not None:
                range_config["gt"] = gt
            if gte is not None:
                range_config["gte"] = gte
            if lt is not None:
                range_config["lt"] = lt
            if lte is not None:
                range_config["lte"] = lte

            clause = {"range": range_config}
            if score:
                clause["range"]["score"] = {"boost": {"value": score}}
            self._clause_list.append(clause)
            return self
        except ValidationError as e:
            raise AtlasSearchError(e)

    def equals(self, path: str, value: Any, score: Optional[float] = None) -> "ClauseBuilder":
        """
        Add an equality clause

        Args:
            path: Field path
            value: Value to match
            score: Score boost value

        Returns:
            Self for chaining
        """
        validate_string_not_empty(path, "equals path")

        clause = {"equals": {"path": path, "value": value}}
        if score:
            clause["equals"]["score"] = {"boost": {"value": score}}
        self._clause_list.append(clause)
        return self

    def exists(self, path: str, score: Optional[float] = None) -> "ClauseBuilder":
        """
        Add an exists clause

        Args:
            path: Field path
            score: Score boost value

        Returns:
            Self for chaining
        """
        validate_string_not_empty(path, "exists path")

        clause = {"exists": {"path": path}}
        if score:
            clause["exists"]["score"] = {"boost": {"value": score}}
        self._clause_list.append(clause)
        return self

    def autocomplete(
        self,
        query: str,
        path: str,
        fuzzy: Optional[Dict[str, Any]] = None,
        score: Optional[float] = None,
    ) -> "ClauseBuilder":
        """
        Add an autocomplete clause

        Args:
            query: Query text
            path: Field path
            fuzzy: Fuzzy matching configuration
            score: Score boost value

        Returns:
            Self for chaining
        """
        validate_string_not_empty(query, "autocomplete query")
        validate_string_not_empty(path, "autocomplete path")

        clause = {"autocomplete": {"query": query, "path": path}}
        if fuzzy:
            clause["autocomplete"]["fuzzy"] = fuzzy
        if score:
            clause["autocomplete"]["score"] = {"boost": {"value": score}}
        self._clause_list.append(clause)
        return self

    def compound(self, compound_builder: "CompoundBuilder") -> "ClauseBuilder":
        """
        Add a nested compound clause

        Args:
            compound_builder: CompoundBuilder to nest

        Returns:
            Self for chaining
        """
        self._clause_list.append({"compound": compound_builder.build()})
        return self

    def raw(self, clause: Dict[str, Any]) -> "ClauseBuilder":
        """
        Add a raw clause for any Atlas Search operator

        Args:
            clause: Raw clause dictionary

        Returns:
            Self for chaining
        """
        if not clause:
            raise AtlasSearchError("raw() requires a non-empty clause")

        self._clause_list.append(clause)
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build into the parent

        Returns:
            Parent compound query
        """
        return self._parent.build()

    def end(self) -> "CompoundBuilder":
        """
        Return to the parent CompoundBuilder for further chaining

        Returns:
            Parent CompoundBuilder
        """
        return self._parent


class AtlasSearchBuilder:
    """
    MongoDB Atlas Search Query Builder
    
    Provides a fluent interface for building Atlas Search queries with support
    for various search operators, compound queries, and faceting.
    
    Examples:
        # Simple text search
        >>> search = AtlasSearchBuilder()\\
        ...     .text("search term", path="title")\\
        ...     .build()
        
        # Using CompoundBuilder for complex queries
        >>> compound = CompoundBuilder()
        >>> compound.must().text("python", path="skills")
        >>> compound.should().text("senior", path="level", score=2.0)
        >>> compound.filter().range("experience", gte=3)
        >>> search = AtlasSearchBuilder()\\
        ...     .compound(compound)\\
        ...     .facet("departments", type="string", path="department")\\
        ...     .build()
        
        # Autocomplete search
        >>> search = AtlasSearchBuilder()\\
        ...     .autocomplete("user inp", path="name", fuzzy={"maxEdits": 2})\\
        ...     .build()
        
        # Facet operator with operator and facets
        >>> compound = CompoundBuilder()
        >>> compound.must().equals("userId", ObjectId('...'))
        >>> search = AtlasSearchBuilder(index="messages")\\
        ...     .use_facet_operator(compound)\\
        ...     .facet("messageType", type="string", path="type")\\
        ...     .build_meta_stage()
    """

    def __init__(self, index: str = "default"):
        """
        Initialize a new AtlasSearchBuilder

        Args:
            index: Name of the Atlas Search index to use
        """
        self._search: Dict[str, Any] = {"index": index}
        self._compound_builder: Optional[CompoundBuilder] = None
        self._facets: Dict[str, Any] = {}
        self._use_facet_operator: bool = False
        self._facet_operator: Optional[Dict[str, Any]] = None

    def text(
        self,
        query: str,
        path: Union[str, List[str]],
        fuzzy: Optional[Dict[str, Any]] = None,
        score: Optional[float] = None,
    ) -> "AtlasSearchBuilder":
        """
        Add text search operator

        Args:
            query: Search query text
            path: Field path(s) to search
            fuzzy: Fuzzy matching configuration
            score: Score boost value

        Returns:
            Self for chaining

        Examples:
            >>> .text("search term", path="title")
            >>> .text("search term", path=["title", "content"], fuzzy={"maxEdits": 1})
        """
        validate_string_not_empty(query, "text query")
        if not path:
            raise AtlasSearchError("text() requires a path")

        search_config = {"query": query, "path": path}
        if fuzzy:
            search_config["fuzzy"] = fuzzy
        if score:
            search_config["score"] = {"boost": {"value": score}}

        self._search["text"] = search_config
        return self

    def phrase(
        self, query: str, path: Union[str, List[str]], slop: int = 0, score: Optional[float] = None
    ) -> "AtlasSearchBuilder":
        """
        Add phrase search operator

        Args:
            query: Phrase to search for
            path: Field path(s) to search
            slop: Maximum distance between terms
            score: Score boost value

        Returns:
            Self for chaining

        Example:
            >>> .phrase("exact phrase", path="content", slop=2)
        """
        validate_string_not_empty(query, "phrase query")
        if not path:
            raise AtlasSearchError("phrase() requires a path")

        search_config = {"query": query, "path": path, "slop": slop}
        if score:
            search_config["score"] = {"boost": {"value": score}}

        self._search["phrase"] = search_config
        return self

    def autocomplete(
        self, query: str, path: str, max_terms: int = 50, fuzzy: Optional[Dict[str, Any]] = None
    ) -> "AtlasSearchBuilder":
        """
        Add autocomplete search operator

        Args:
            query: Query text
            path: Field path
            max_terms: Maximum number of terms to match
            fuzzy: Fuzzy matching configuration

        Returns:
            Self for chaining

        Example:
            >>> .autocomplete("user inp", path="name", fuzzy={"maxEdits": 2})
        """
        validate_string_not_empty(query, "autocomplete query")
        validate_string_not_empty(path, "autocomplete path")

        search_config = {
            "query": query,
            "path": path,
            "tokenOrder": "sequential",
            "fuzzy": fuzzy or {},
        }
        if max_terms != 50:
            search_config["maxTerms"] = max_terms

        self._search["autocomplete"] = search_config
        return self

    def regex(
        self, query: str, path: Union[str, List[str]], allow_analyzed_field: bool = False
    ) -> "AtlasSearchBuilder":
        """
        Add regex search operator

        Args:
            query: Regex pattern
            path: Field path(s) to search
            allow_analyzed_field: Allow searching analyzed fields

        Returns:
            Self for chaining

        Example:
            >>> .regex(".*pattern.*", path="field")
        """
        validate_string_not_empty(query, "regex query")
        if not path:
            raise AtlasSearchError("regex() requires a path")

        search_config = {"query": query, "path": path, "allowAnalyzedField": allow_analyzed_field}
        self._search["regex"] = search_config
        return self

    def wildcard(
        self, query: str, path: Union[str, List[str]], allow_analyzed_field: bool = False
    ) -> "AtlasSearchBuilder":
        """
        Add wildcard search operator (* and ? supported)

        Args:
            query: Wildcard query
            path: Field path(s) to search
            allow_analyzed_field: Allow searching analyzed fields

        Returns:
            Self for chaining

        Example:
            >>> .wildcard("test*", path="field")
        """
        validate_string_not_empty(query, "wildcard query")
        if not path:
            raise AtlasSearchError("wildcard() requires a path")

        search_config = {"query": query, "path": path, "allowAnalyzedField": allow_analyzed_field}
        self._search["wildcard"] = search_config
        return self

    def range(
        self, path: str, gt: Any = None, gte: Any = None, lt: Any = None, lte: Any = None
    ) -> "AtlasSearchBuilder":
        """
        Add range search operator

        Args:
            path: Field path
            gt: Greater than value
            gte: Greater than or equal value
            lt: Less than value
            lte: Less than or equal value

        Returns:
            Self for chaining

        Example:
            >>> .range(path="price", gte=10, lte=100)
        """
        validate_string_not_empty(path, "range path")
        validate_at_least_one(gt, gte, lt, lte, context="At least one range boundary")

        range_config = {"path": path}
        if gt is not None:
            range_config["gt"] = gt
        if gte is not None:
            range_config["gte"] = gte
        if lt is not None:
            range_config["lt"] = lt
        if lte is not None:
            range_config["lte"] = lte

        self._search["range"] = range_config
        return self

    def compound(self, compound_builder: CompoundBuilder) -> "AtlasSearchBuilder":
        """
        Use a CompoundBuilder for complex queries

        Args:
            compound_builder: CompoundBuilder with configured clauses

        Returns:
            Self for chaining

        Example:
            >>> compound = CompoundBuilder()
            >>> compound.must().text("required", path="field")
            >>> compound.should().text("optional", path="field")
            >>> search = AtlasSearchBuilder().compound(compound)
        """
        self._compound_builder = compound_builder
        return self

    def use_facet_operator(
        self, operator: Union[CompoundBuilder, Dict[str, Any], None] = None
    ) -> "AtlasSearchBuilder":
        """
        Enable facet operator mode where the search uses the 'facet' operator 
        with 'operator' and 'facets' fields. This is useful when you want to 
        apply faceting with a specific operator.
        
        Args:
            operator: Can be a CompoundBuilder, a raw operator dict, or None to 
                     use previously set compound
        
        Returns:
            Self for chaining
            
        Example:
            >>> compound = CompoundBuilder()
            >>> compound.must().equals("userId", ObjectId('...'))
            >>> compound.must().text("success", path="status")
            >>> search = AtlasSearchBuilder(index="messages")\\
            ...     .use_facet_operator(compound)\\
            ...     .facet("messageType", type="string", path="type")\\
            ...     .build_meta_stage()
        """
        self._use_facet_operator = True

        if operator is not None:
            if isinstance(operator, CompoundBuilder):
                self._facet_operator = {"compound": operator.build()}
            else:
                self._facet_operator = operator
        elif self._compound_builder:
            # Use previously set compound builder
            self._facet_operator = {"compound": self._compound_builder.build()}

        return self

    def more_like_this(
        self, like: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> "AtlasSearchBuilder":
        """
        Add moreLikeThis search operator (find similar documents)

        Args:
            like: Document(s) to find similar results for

        Returns:
            Self for chaining

        Example:
            >>> .more_like_this(like={"title": "Example Title", "content": "Example content"})
        """
        if not like:
            raise AtlasSearchError("more_like_this() requires like parameter")

        self._search["moreLikeThis"] = {"like": like}
        return self

    def facet(
        self,
        name: str,
        type: str = "string",
        path: Optional[str] = None,
        num_buckets: int = 10,
        boundaries: Optional[List] = None,
    ) -> "AtlasSearchBuilder":
        """
        Add facet for aggregations

        Args:
            name: Facet name
            type: Facet type ("string", "number", "date")
            path: Field path
            num_buckets: Number of buckets (for string facets)
            boundaries: Bucket boundaries (for number/date facets)

        Returns:
            Self for chaining

        Examples:
            >>> .facet("categories", type="string", path="category")
            >>> .facet("price_ranges", type="number", path="price", boundaries=[0, 50, 100, 200])
        """
        validate_string_not_empty(name, "facet name")

        facet_config = {"type": type}

        if path:
            facet_config["path"] = path

        if type == "number" and boundaries:
            facet_config["boundaries"] = boundaries
        elif type == "string":
            facet_config["numBuckets"] = num_buckets

        self._facets[name] = facet_config
        return self

    def score_function(self, function: str, **params) -> "AtlasSearchBuilder":
        """
        Apply scoring function

        Args:
            function: Function name (e.g., "multiply", "log")
            **params: Function parameters

        Returns:
            Self for chaining

        Examples:
            >>> .score_function("multiply", factor=2.0)
            >>> .score_function("log", offset=1)
        """
        validate_string_not_empty(function, "score function")

        if "score" not in self._search:
            self._search["score"] = {}

        self._search["score"]["function"] = {function: params}
        return self

    def count(
        self, type: str = "lowerBound", threshold: Optional[int] = None
    ) -> "AtlasSearchBuilder":
        """
        Configure count options

        Args:
            type: Count type ("lowerBound" or "total")
            threshold: Threshold for accurate counting

        Returns:
            Self for chaining

        Example:
            >>> .count(type="total")  # or "lowerBound"
        """
        count_config = {"type": type}
        if threshold:
            count_config["threshold"] = threshold

        self._search["count"] = count_config
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build the final Atlas Search query

        Returns:
            Dictionary representing the Atlas Search query
        """
        if self._use_facet_operator:
            # Build using facet operator structure
            facet_config = {}

            if self._facet_operator:
                facet_config["operator"] = self._facet_operator

            if self._facets:
                facet_config["facets"] = self._facets

            self._search["facet"] = facet_config
        else:
            # Standard build
            if self._compound_builder:
                self._search["compound"] = self._compound_builder.build()

            if self._facets:
                self._search["facets"] = self._facets

        return self._search

    def build_stage(self) -> Dict[str, Any]:
        """
        Build as aggregation pipeline stage ($search)

        Returns:
            Dictionary with $search operator
        """
        return {AggregateOperator.SEARCH: self.build()}

    def build_meta_stage(self) -> Dict[str, Any]:
        """
        Build as $searchMeta stage (for counting/faceting without documents)

        Returns:
            Dictionary with $searchMeta operator
        """
        return {AggregateOperator.SEARCH_META: self.build()}

    def __repr__(self):
        return f"AtlasSearchBuilder(index={self._search.get('index')})"


__all__ = [
    "AtlasSearchBuilder",
    "CompoundBuilder",
    "ClauseBuilder",
]
