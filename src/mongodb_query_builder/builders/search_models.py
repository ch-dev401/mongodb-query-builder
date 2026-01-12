"""
Declarative Search Models for MongoDB Atlas Search

Provides a class-based approach to defining Atlas Search configurations
with field-level index and facet settings.
"""

from typing import Any, Dict, List, Optional, Type, Union

from .atlas_search_builder import AtlasSearchBuilder, CompoundBuilder


class IndexField:
    """
    Defines configuration for an Atlas Search indexed field.
    
    Args:
        string_index: Enable text/string indexing for search
        string_facet: Enable string faceting for aggregations
        number_index: Enable numeric indexing
        number_facet: Enable numeric faceting
        date_index: Enable date indexing
        date_facet: Enable date faceting
        
    Examples:
        >>> type_field = IndexField(string_index=True, string_facet=True)
        >>> price_field = IndexField(number_index=True, number_facet=True)
        >>> created_field = IndexField(date_index=True, date_facet=True)
    """

    def __init__(
        self,
        string_index: bool = False,
        string_facet: bool = False,
        number_index: bool = False,
        number_facet: bool = False,
        date_index: bool = False,
        date_facet: bool = False,
    ):
        self.string_index = string_index
        self.string_facet = string_facet
        self.number_index = number_index
        self.number_facet = number_facet
        self.date_index = date_index
        self.date_facet = date_facet

    @property
    def is_searchable(self) -> bool:
        """Check if field is searchable"""
        return self.string_index or self.number_index or self.date_index

    @property
    def is_facetable(self) -> bool:
        """Check if field supports faceting"""
        return self.string_facet or self.number_facet or self.date_facet

    @property
    def facet_type(self) -> Optional[str]:
        """Get the facet type for this field"""
        if self.string_facet:
            return "string"
        elif self.number_facet:
            return "number"
        elif self.date_facet:
            return "date"
        return None

    @property
    def search_type(self) -> Optional[str]:
        """Get the search type for this field"""
        if self.string_index:
            return "string"
        elif self.number_index:
            return "number"
        elif self.date_index:
            return "date"
        return None

    def __repr__(self):
        parts = []
        if self.string_index:
            parts.append("string_index")
        if self.string_facet:
            parts.append("string_facet")
        if self.number_index:
            parts.append("number_index")
        if self.number_facet:
            parts.append("number_facet")
        if self.date_index:
            parts.append("date_index")
        if self.date_facet:
            parts.append("date_facet")
        return f"IndexField({', '.join(f'{p}=True' for p in parts)})"


class SearchModelMeta(type):
    """
    Metaclass that collects field definitions from class attributes.
    
    Processes both direct class attributes and a 'fields' dictionary
    to support field names with special characters (like dots).
    """

    def __new__(mcs, name, bases, namespace):
        # Collect field definitions from class attributes
        fields = {}
        
        # First, check for a 'fields' dictionary (supports any field name)
        if "fields" in namespace and isinstance(namespace["fields"], dict):
            fields.update(namespace["fields"])
        
        # Then collect IndexField instances from class attributes
        for key, value in list(namespace.items()):
            if isinstance(value, IndexField) and key != "fields":
                fields[key] = value
                # Remove from namespace to prevent attribute access issues
                del namespace[key]

        # Store fields in _fields attribute
        namespace["_fields"] = fields

        # Ensure index name exists
        if "index" not in namespace:
            namespace["index"] = "default"

        return super().__new__(mcs, name, bases, namespace)


class SearchModel(metaclass=SearchModelMeta):
    """
    Base class for declarative Atlas Search models.
    
    Define your search schema by subclassing and adding IndexField definitions:
    
    Examples:
        >>> class UserSearch(SearchModel):
        ...     index = "users"
        ...     
        ...     # Using class attributes for simple field names
        ...     name = IndexField(string_index=True, string_facet=True)
        ...     age = IndexField(number_index=True, number_facet=True)
        ...     status = IndexField(string_index=True)
        
        >>> class MessageSearch(SearchModel):
        ...     index = "messages"
        ...     
        ...     # Using fields dict for names with special characters
        ...     fields = {
        ...         "type": IndexField(string_facet=True, string_index=True),
        ...         "rawData.from": IndexField(string_facet=True, string_index=True),
        ...         "status": IndexField(string_index=True),
        ...     }
    """

    index: str = "default"
    _fields: Dict[str, IndexField] = {}

    def __init__(self):
        """Initialize with a new builder instance"""
        self._builder = AtlasSearchBuilder(index=self.index)

    @classmethod
    def search(cls) -> "SearchQuery":
        """
        Start building a search query.
        
        Returns:
            SearchQuery instance for building queries
            
        Example:
            >>> results = MessageSearch.search()\\
            ...     .text("hello", field="type")\\
            ...     .facet("status")\\
            ...     .build()
        """
        return SearchQuery(cls)

    @classmethod
    def builder(cls) -> AtlasSearchBuilder:
        """
        Get a raw AtlasSearchBuilder for advanced use cases.
        
        Returns:
            AtlasSearchBuilder configured with this model's index
        """
        return AtlasSearchBuilder(index=cls.index)

    @classmethod
    def get_field(cls, field_name: str) -> Optional[IndexField]:
        """
        Get field configuration by name.
        
        Args:
            field_name: Field name (supports dot notation)
            
        Returns:
            IndexField configuration or None
        """
        return cls._fields.get(field_name)

    @classmethod
    def get_searchable_fields(cls) -> Dict[str, IndexField]:
        """
        Get all fields that are searchable.
        
        Returns:
            Dictionary of field names to IndexField configs
        """
        return {k: v for k, v in cls._fields.items() if v.is_searchable}

    @classmethod
    def get_facetable_fields(cls) -> Dict[str, IndexField]:
        """
        Get all fields that support faceting.
        
        Returns:
            Dictionary of field names to IndexField configs
        """
        return {k: v for k, v in cls._fields.items() if v.is_facetable}

    @classmethod
    def validate_field(cls, field_name: str, operation: str) -> None:
        """
        Validate that a field supports a specific operation.
        
        Args:
            field_name: Field name to validate
            operation: Operation type ('search', 'facet')
            
        Raises:
            ValueError: If field doesn't support the operation
        """
        field = cls.get_field(field_name)
        if field is None:
            raise ValueError(f"Field '{field_name}' is not defined in {cls.__name__}")

        if operation == "search" and not field.is_searchable:
            raise ValueError(f"Field '{field_name}' is not configured for search operations")
        elif operation == "facet" and not field.is_facetable:
            raise ValueError(f"Field '{field_name}' is not configured for faceting")

    @classmethod
    def get_all_fields(cls) -> Dict[str, IndexField]:
        """
        Get all defined fields.
        
        Returns:
            Dictionary of all field configurations
        """
        return cls._fields.copy()


class SearchQuery:
    """
    Query builder that integrates with SearchModel for type-safe queries.
    
    Provides validation and convenience methods based on the model's field definitions.
    """

    def __init__(self, model_class: Type[SearchModel]):
        """
        Initialize query builder.
        
        Args:
            model_class: SearchModel subclass to build queries for
        """
        self.model_class = model_class
        self._builder = AtlasSearchBuilder(index=model_class.index)

    def text(
        self,
        query: str,
        field: str,
        fuzzy: Optional[Dict[str, Any]] = None,
        score: Optional[float] = None,
    ) -> "SearchQuery":
        """
        Add text search for a field.
        
        Args:
            query: Search query text
            field: Field name (must be string_index=True)
            fuzzy: Fuzzy matching configuration
            score: Score boost value
            
        Returns:
            Self for chaining
            
        Raises:
            ValueError: If field isn't configured for text search
        """
        self.model_class.validate_field(field, "search")
        field_config = self.model_class.get_field(field)
        
        if not field_config.string_index:
            raise ValueError(f"Field '{field}' must have string_index=True for text search")
        
        self._builder.text(query, path=field, fuzzy=fuzzy, score=score)
        return self

    def phrase(
        self,
        query: str,
        field: str,
        slop: int = 0,
        score: Optional[float] = None,
    ) -> "SearchQuery":
        """
        Add phrase search for a field.
        
        Args:
            query: Phrase to search
            field: Field name
            slop: Maximum distance between terms
            score: Score boost value
            
        Returns:
            Self for chaining
        """
        self.model_class.validate_field(field, "search")
        self._builder.phrase(query, path=field, slop=slop, score=score)
        return self

    def autocomplete(
        self,
        query: str,
        field: str,
        fuzzy: Optional[Dict[str, Any]] = None,
    ) -> "SearchQuery":
        """
        Add autocomplete search.
        
        Args:
            query: Query text
            field: Field name
            fuzzy: Fuzzy matching configuration
            
        Returns:
            Self for chaining
        """
        self.model_class.validate_field(field, "search")
        self._builder.autocomplete(query, path=field, fuzzy=fuzzy)
        return self

    def compound(self, compound_builder: CompoundBuilder) -> "SearchQuery":
        """
        Use a compound query builder.
        
        Args:
            compound_builder: Configured CompoundBuilder
            
        Returns:
            Self for chaining
        """
        self._builder.compound(compound_builder)
        return self

    def facet(
        self,
        field: str,
        num_buckets: int = 10,
        boundaries: Optional[List] = None,
    ) -> "SearchQuery":
        """
        Add facet for a field.
        
        Args:
            field: Field name (must be facetable)
            num_buckets: Number of buckets for string facets
            boundaries: Boundaries for number/date facets
            
        Returns:
            Self for chaining
            
        Raises:
            ValueError: If field isn't configured for faceting
        """
        self.model_class.validate_field(field, "facet")
        field_config = self.model_class.get_field(field)
        
        facet_type = field_config.facet_type
        self._builder.facet(
            field,
            type=facet_type,
            path=field,
            num_buckets=num_buckets,
            boundaries=boundaries,
        )
        return self

    def facet_all(self, **kwargs) -> "SearchQuery":
        """
        Add facets for all facetable fields.
        
        Args:
            **kwargs: Additional facet configuration
            
        Returns:
            Self for chaining
        """
        for field_name, field_config in self.model_class.get_facetable_fields().items():
            self._builder.facet(field_name, type=field_config.facet_type, path=field_name, **kwargs)
        return self

    def use_facet_operator(
        self, operator: Union[CompoundBuilder, Dict[str, Any], None] = None
    ) -> "SearchQuery":
        """
        Enable facet operator mode.
        
        Args:
            operator: Operator configuration
            
        Returns:
            Self for chaining
        """
        self._builder.use_facet_operator(operator)
        return self

    def count(
        self, type: str = "lowerBound", threshold: Optional[int] = None
    ) -> "SearchQuery":
        """
        Configure count options.
        
        Args:
            type: Count type ("lowerBound" or "total")
            threshold: Threshold for accurate counting
            
        Returns:
            Self for chaining
        """
        self._builder.count(type=type, threshold=threshold)
        return self

    def raw_builder(self) -> AtlasSearchBuilder:
        """
        Get the underlying AtlasSearchBuilder for advanced operations.
        
        Returns:
            The underlying builder instance
        """
        return self._builder

    def build(self) -> Dict[str, Any]:
        """
        Build the search query.
        
        Returns:
            Query dictionary
        """
        return self._builder.build()

    def build_stage(self) -> Dict[str, Any]:
        """
        Build as aggregation pipeline stage.
        
        Returns:
            $search stage dictionary
        """
        return self._builder.build_stage()

    def build_meta_stage(self) -> Dict[str, Any]:
        """
        Build as $searchMeta stage.
        
        Returns:
            $searchMeta stage dictionary
        """
        return self._builder.build_meta_stage()


__all__ = [
    "IndexField",
    "SearchModel",
    "SearchQuery",
    "SearchModelMeta",
]