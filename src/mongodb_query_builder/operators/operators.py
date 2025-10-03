"""
MongoDB Query and Aggregation Operators

This module defines all MongoDB operators used in queries and aggregations.
"""


class Operator:
    """MongoDB Query Operators"""

    # Comparison Operators
    EQ = "$eq"
    NE = "$ne"
    GT = "$gt"
    GTE = "$gte"
    LT = "$lt"
    LTE = "$lte"
    IN = "$in"
    NIN = "$nin"

    # Logical Operators
    AND = "$and"
    OR = "$or"
    NOT = "$not"
    NOR = "$nor"

    # Element Operators
    EXISTS = "$exists"
    TYPE = "$type"

    # Evaluation Operators
    REGEX = "$regex"
    OPTIONS = "$options"
    TEXT = "$text"
    WHERE = "$where"
    EXPR = "$expr"
    JSON_SCHEMA = "$jsonSchema"
    MOD = "$mod"

    # Array Operators
    ALL = "$all"
    ELEM_MATCH = "$elemMatch"
    SIZE = "$size"

    # Bitwise Operators
    BITS_ALL_CLEAR = "$bitsAllClear"
    BITS_ALL_SET = "$bitsAllSet"
    BITS_ANY_CLEAR = "$bitsAnyClear"
    BITS_ANY_SET = "$bitsAnySet"

    # Geospatial Operators
    GEO_WITHIN = "$geoWithin"
    GEO_INTERSECTS = "$geoIntersects"
    NEAR = "$near"
    NEAR_SPHERE = "$nearSphere"


class AggregateOperator:
    """MongoDB Aggregation Pipeline Operators"""

    # Pipeline Stages
    ADD_FIELDS = "$addFields"
    BUCKET = "$bucket"
    BUCKET_AUTO = "$bucketAuto"
    COLL_STATS = "$collStats"
    COUNT = "$count"
    FACET = "$facet"
    GEO_NEAR = "$geoNear"
    GRAPH_LOOKUP = "$graphLookup"
    GROUP = "$group"
    INDEX_STATS = "$indexStats"
    LIMIT = "$limit"
    LOOKUP = "$lookup"
    MATCH = "$match"
    MERGE = "$merge"
    OUT = "$out"
    PROJECT = "$project"
    REDACT = "$redact"
    REPLACE_ROOT = "$replaceRoot"
    REPLACE_WITH = "$replaceWith"
    SAMPLE = "$sample"
    SEARCH = "$search"
    SEARCH_META = "$searchMeta"
    SET = "$set"
    SET_WINDOW_FIELDS = "$setWindowFields"
    SKIP = "$skip"
    SORT = "$sort"
    SORT_BY_COUNT = "$sortByCount"
    UNION_WITH = "$unionWith"
    UNSET = "$unset"
    UNWIND = "$unwind"

    # Accumulator Operators (for $group)
    AVG = "$avg"
    FIRST = "$first"
    LAST = "$last"
    MAX = "$max"
    MIN = "$min"
    PUSH = "$push"
    ADD_TO_SET = "$addToSet"
    STD_DEV_POP = "$stdDevPop"
    STD_DEV_SAMP = "$stdDevSamp"
    SUM = "$sum"

    # Expression Operators
    ABS = "$abs"
    CONCAT = "$concat"
    COND = "$cond"
    DATE_TO_STRING = "$dateToString"
    DAY_OF_MONTH = "$dayOfMonth"
    DAY_OF_WEEK = "$dayOfWeek"
    DAY_OF_YEAR = "$dayOfYear"
    HOUR = "$hour"
    MILLISECOND = "$millisecond"
    MINUTE = "$minute"
    MONTH = "$month"
    SECOND = "$second"
    WEEK = "$week"
    YEAR = "$year"
    LITERAL = "$literal"
    MAP = "$map"
    REDUCE = "$reduce"
    SIZE_OP = "$size"
    SLICE = "$slice"
    SPLIT = "$split"
    STR_LEN_CP = "$strLenCP"
    SUBSTR = "$substr"
    TO_LOWER = "$toLower"
    TO_UPPER = "$toUpper"


class UpdateOperator:
    """MongoDB Update Operators"""

    # Field Update Operators
    SET = "$set"
    UNSET = "$unset"
    SET_ON_INSERT = "$setOnInsert"
    INC = "$inc"
    MUL = "$mul"
    MIN = "$min"
    MAX = "$max"
    CURRENT_DATE = "$currentDate"
    RENAME = "$rename"

    # Array Update Operators
    ADD_TO_SET = "$addToSet"
    POP = "$pop"
    PULL = "$pull"
    PUSH = "$push"
    PULL_ALL = "$pullAll"

    # Array Update Modifiers
    EACH = "$each"
    POSITION = "$position"
    SLICE = "$slice"
    SORT = "$sort"

    # Bitwise Update Operator
    BIT = "$bit"


__all__ = [
    "Operator",
    "AggregateOperator",
    "UpdateOperator",
]
