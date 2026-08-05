import re
import logging
from typing import Iterable, Optional, Union
from functools import lru_cache
from datetime import datetime, date

from prefixdate.precision import Precision
from prefixdate.parse import DatePrefix, Raw

log = logging.getLogger(__name__)

MONTH_FORMATS = re.compile(r"(%b|%B|%m|%c|%x)")
DAY_FORMATS = re.compile(r"(%d|%w|%c|%x)")
HOUR_FORMATS = re.compile(r"(%H|%I|%c|%X)")
MINUTE_FORMATS = re.compile(r"(%M|%c|%X)")
SECOND_FORMATS = re.compile(r"(%S|%c|%X)")


@lru_cache(maxsize=1000)
def format_precision(format: str) -> Precision:
    """Determine the precision of a `datetime.strptime` format string so that it
    can be used in constructing a `DatePrefix`. This will check if the format
    string mentions directives with increasing precision. A format string that
    defines no date but only time directives will be considered `Precision.EMPTY`.
    """
    if MONTH_FORMATS.search(format) is None:
        return Precision.YEAR
    if DAY_FORMATS.search(format) is None:
        return Precision.MONTH
    if HOUR_FORMATS.search(format) is None:
        return Precision.DAY
    if MINUTE_FORMATS.search(format) is None:
        return Precision.HOUR
    if SECOND_FORMATS.search(format) is None:
        return Precision.MINUTE
    return Precision.SECOND


@lru_cache(maxsize=1000)
def has_two_digit_year(format: str) -> bool:
    """Check if a `datetime.strptime` format string reads the year as two digits."""
    return "%y" in format.replace("%%", "")


def resolve_two_digit_year(dt: datetime, base_year: Union[int, date]) -> datetime:
    """Read the two-digit year of a parsed date as the first year, not before
    `base_year`, that ends in the same two digits.

    `strptime` reads two-digit years 00-68 as 20xx and 69-99 as 19xx, so a date
    outside of that fixed window ends up in the wrong century. The base year
    replaces that window with one the caller chooses. It is given as a year
    number, or as a date on 1 January of that year.

    Raises `ValueError` if the base year is a date other than 1 January, or if the
    resolved date does not exist, i.e. 29 February in a year which is not a leap
    year.
    """
    if isinstance(base_year, date):
        if (base_year.month, base_year.day) != (1, 1):
            raise ValueError(f"Base year is not 1 January: {base_year}")
        base_year = base_year.year
    # "68" with base year 1926 gives 1968, and "24" with base year 1926 gives 2024.
    # 29 February in a year which is not a leap year raises, rather than moving to
    # another century: either the base year or the source value is wrong, and only
    # a human can tell which.
    return dt.replace(year=base_year + (dt.year - base_year) % 100)


def parse_format(
    raw: Raw, format: str, two_digit_year_base: Optional[Union[int, date]] = None
) -> DatePrefix:
    """Parse the given raw input using the supplied format string. The precision of the
    result is inferred from the format string. On success, the format string is set as
    the `format` attribute of the result.

    `two_digit_year_base` is the earliest year a two-digit year may denote, given as
    a year number or as a date on 1 January of that year. A date parsed by a format
    that contains `%y` moves into the century that places it in the 100 years from
    that year, instead of using the fixed 1969-2068 window of `strptime`. Parsing
    such a format without a base year logs a warning.
    """
    if isinstance(raw, int):
        raw = str(raw)
    elif isinstance(raw, (datetime, date, DatePrefix)):
        return DatePrefix(raw)
    elif raw is None:
        return DatePrefix(None, precision=Precision.EMPTY)
    try:
        dt = datetime.strptime(raw, format)
        precision = format_precision(format)
        if has_two_digit_year(format):
            if two_digit_year_base is None:
                log.warning(
                    "Date %r is parsed with the two-digit year format %s and no "
                    "base year, so it may be in the wrong century",
                    raw,
                    format,
                )
            else:
                dt = resolve_two_digit_year(dt, two_digit_year_base)
        prefix = DatePrefix(dt, precision=precision)
        prefix.format = format
        return prefix
    except (ValueError, TypeError):
        log.warning("Date %r does not match format %s", raw, format)
    return DatePrefix(None, precision=Precision.EMPTY)


def parse_formats(
    raw: Raw,
    formats: Iterable[str],
    two_digit_year_base: Optional[Union[int, date]] = None,
) -> DatePrefix:
    """Run `parse_format` using an iterable of format strings, returning the
    first non-empty result from parsing."""
    prefix = DatePrefix(None, precision=Precision.EMPTY)
    for format in formats:
        prefix = parse_format(raw, format, two_digit_year_base=two_digit_year_base)
        if prefix.precision != Precision.EMPTY:
            return prefix
    return prefix
