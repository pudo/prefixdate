from prefixdate.formats import parse_format, parse_formats, format_precision, Precision


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
