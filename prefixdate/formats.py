import logging
import re
from collections.abc import Iterable
from datetime import date, datetime
from functools import lru_cache

from prefixdate.parse import DatePrefix, Raw
from prefixdate.precision import Precision

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


def resolve_two_digit_year(dt: datetime, base_year: int) -> datetime:
    """Read a two-digit year in the 100 years that start at `base_year`. A base
    year of 1926 means that "68" is 1968 and "24" is 2024.

    `strptime` instead reads 00-68 as 20xx and 69-99 as 19xx, so a date outside of
    that fixed window ends up in the wrong century.

    Raises `ValueError` if the resolved date does not exist, i.e. 29 February in a
    year which is not a leap year.
    """
    return dt.replace(year=base_year + (dt.year - base_year) % 100)


def parse_format(
    raw: Raw, format: str, two_digit_year_base: int | None = None
) -> DatePrefix:
    """Parse the given raw input using the supplied format string. The precision of the
    result is inferred from the format string.

    `two_digit_year_base` is the first year of the 100 years that a `%y` format is
    read in: a base year of 1926 reads "68" as 1968 and "24" as 2024. Without it,
    `strptime`'s fixed 1969-2068 window applies and a warning is logged.
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
        return DatePrefix(dt, precision=precision)
    except (ValueError, TypeError):
        log.debug("Date %r does not match format %s", raw, format)
    return DatePrefix(None, precision=Precision.EMPTY)


def parse_formats(
    raw: Raw, formats: Iterable[str], two_digit_year_base: int | None = None
) -> DatePrefix:
    """Run `parse_format` using an iterable of format strings, returning the
    first non-empty result from parsing."""
    prefix = DatePrefix(None, precision=Precision.EMPTY)
    for format in formats:
        prefix = parse_format(raw, format, two_digit_year_base=two_digit_year_base)
        if prefix.precision != Precision.EMPTY:
            return prefix
    return prefix
