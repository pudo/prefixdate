from prefixdate.parse import DatePrefix
from prefixdate.precision import Precision


def parse(raw, precision=Precision.FULL):
    """Parse the given input date string and return a `PrefixDate` object
    that holds a datetime, text version and the precision of the date."""
    return DatePrefix(raw, precision=precision)


def normalize_date(raw, precision=Precision.FULL):
    """Take the given input date string and parse it into the normalised
    format to the precision given as an argument."""
    return parse(raw, precision=precision).text


def parse_parts(
    year=None,
    month=None,
    day=None,
    hour=None,
    minute=None,
    second=None,
    precision=Precision.FULL,
):
    """Try to build a date prefix from the date components as given until
    one of them is null."""
    raw = f"{year}-{month}-{day}T{hour}:{minute}:{second}"
    return parse(raw, precision=precision)


__all__ = ["DatePrefix", "Precision", "parse", "parse_parts", "normalize_date"]
__version__ = "0.1.2"
