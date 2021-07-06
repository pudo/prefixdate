from typing import Optional, Union
from prefixdate.parse import DatePrefix, Raw
from prefixdate.precision import Precision

Part = Union[None, str, int]


def parse(raw: Raw, precision: Precision = Precision.FULL) -> DatePrefix:
    """Parse the given input date string and return a `DatePrefix` object
    that holds a datetime, text version and the precision of the date."""
    return DatePrefix(raw, precision=precision)


def normalize_date(raw: Raw, precision: Precision = Precision.FULL) -> Optional[str]:
    """Take the given input date string and parse it into the normalised
    format to the precision given as an argument."""
    return parse(raw, precision=precision).text


def parse_parts(
    year: Part = None,
    month: Part = None,
    day: Part = None,
    hour: Part = None,
    minute: Part = None,
    second: Part = None,
    precision: Precision = Precision.FULL,
) -> DatePrefix:
    """Try to build a date prefix from the date components as given until
    one of them is null."""
    raw = f"{year}-{month}-{day}T{hour}:{minute}:{second}"
    return parse(raw, precision=precision)


__all__ = ["DatePrefix", "Precision", "parse", "parse_parts", "normalize_date"]
__version__ = "0.2.1"
