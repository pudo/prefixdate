from prefixdate.formats import (
    format_precision,
    has_two_digit_year,
    parse_format,
    parse_formats,
    resolve_two_digit_year,
)
from prefixdate.parse import DatePrefix, Raw
from prefixdate.precision import Precision

Part = str | int | None


def parse(raw: Raw, precision: Precision = Precision.FULL) -> DatePrefix:
    """Parse the given input date string and return a `DatePrefix` object
    that holds a datetime, text version and the precision of the date."""
    return DatePrefix(raw, precision=precision)


def normalize_date(raw: Raw, precision: Precision = Precision.FULL) -> str | None:
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


__all__ = [
    "DatePrefix",
    "Precision",
    "format_precision",
    "has_two_digit_year",
    "normalize_date",
    "parse",
    "parse_format",
    "parse_formats",
    "parse_parts",
    "resolve_two_digit_year",
]
__version__ = "0.6.1"
