import re
import logging
from typing import Iterable
from functools import lru_cache
from datetime import datetime, date, timezone

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


def parse_format(raw: Raw, format: str) -> DatePrefix:
    """Parse the given raw input using the supplied format string. The precision of the
    result is inferred from the format string."""
    if isinstance(raw, int):
        raw = str(raw)
    elif isinstance(raw, (datetime, date, DatePrefix)):
        return DatePrefix(raw)
    elif raw is None:
        return DatePrefix(None, precision=Precision.EMPTY)
    try:
        dt = datetime.strptime(raw, format)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        precision = format_precision(format)
        return DatePrefix(dt, precision=precision)
    except (ValueError, TypeError):
        log.warning("Date %r does not match format %s", raw, format)
    return DatePrefix(None, precision=Precision.EMPTY)


def parse_formats(raw: Raw, formats: Iterable[str]) -> DatePrefix:
    """Run `parse_format` using an iterable of format strings, returning the
    first non-empty result from parsing."""
    prefix = DatePrefix(None, precision=Precision.EMPTY)
    for format in formats:
        prefix = parse_format(raw, format)
        if prefix.precision != Precision.EMPTY:
            return prefix
    return prefix
