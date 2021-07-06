from enum import Enum


class Precision(Enum):
    """A date precision, defined by the offset of relevant date parts in an
    ISO 8601 datetime string."""

    EMPTY = 0
    YEAR = 4
    MONTH = 7
    DAY = 10
    HOUR = 13
    MINUTE = 16
    SECOND = 19
    FULL = SECOND
