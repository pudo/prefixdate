from datetime import datetime

from pytest import raises

from prefixdate.formats import (
    Precision,
    format_precision,
    has_two_digit_year,
    parse_format,
    parse_formats,
    resolve_two_digit_year,
)


def test_format_precision():
    assert format_precision("la la %c bla") == Precision.SECOND
    assert format_precision("%Y bla") == Precision.YEAR
    assert format_precision("%m %Y") == Precision.MONTH
    assert format_precision("%d %b %Y") == Precision.DAY
    assert format_precision("%Y-%m-%dXX%H") == Precision.HOUR
    assert format_precision("%Y%m%d%H%M") == Precision.MINUTE


def test_parse_format():
    prefix = parse_format("2021 bla", "%Y bla")
    assert prefix.text == "2021"
    assert prefix.precision == Precision.YEAR
    second = parse_format(prefix, "%Y bla")
    assert second == prefix
    prefix = parse_format("2021 blubb", "%Y bla")
    assert prefix.text is None
    prefix = parse_format(None, "%Y bla")
    assert prefix.text is None
    prefix = parse_format(20210110, "%Y%m%d")
    assert prefix.text == "2021-01-10"
    assert prefix.precision == Precision.DAY


def test_parse_formats():
    prefix = parse_formats(None, ["%Y bla"])
    assert prefix.text is None

    prefix = parse_formats("2021", [])
    assert prefix.text is None

    prefix = parse_formats("2021", ["%Y"])
    assert prefix.text == "2021"

    prefix = parse_formats("2021", ["%Y-%m", "%Y"])
    assert prefix.text == "2021"


def test_has_two_digit_year():
    assert has_two_digit_year("%d-%m-%y")
    assert has_two_digit_year("%y")
    assert not has_two_digit_year("%d-%m-%Y")
    assert not has_two_digit_year("%Y")
    # A literal percent sign followed by "y" is not a directive.
    assert not has_two_digit_year("%d %%y")


def test_two_digit_year_base():
    # Without a base year, the fixed strptime window applies.
    assert parse_format("16-07-68", "%d-%m-%y").text == "2068-07-16"

    # The base year selects the century.
    assert parse_format("16-07-68", "%d-%m-%y", 1926).text == "1968-07-16"
    assert parse_format("16-07-24", "%d-%m-%y", 1926).text == "2024-07-16"
    assert parse_format("16-07-68", "%d-%m-%y", 2000).text == "2068-07-16"

    # Reduced precision is kept.
    assert parse_format("07-68", "%m-%y", 1926).text == "1968-07"
    assert parse_format("68", "%y", 1926).text == "1968"

    # A four-digit year keeps its century.
    assert parse_format("16-07-1868", "%d-%m-%Y", 1926).text == "1868-07-16"

    # 29 February in a year which is not a leap year does not resolve at all:
    # 1900 does not exist, and guessing another century would hide the problem.
    assert parse_format("29-02-00", "%d-%m-%y", 1850).text is None
    with raises(ValueError):
        resolve_two_digit_year(datetime(2000, 2, 29), 1850)

    # The base year reaches parse_format through parse_formats.
    prefix = parse_formats("16-07-68", ["%Y-%m-%d", "%d-%m-%y"], 1926)
    assert prefix.text == "1968-07-16"
