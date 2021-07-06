from datetime import datetime, timezone
from prefixdate import parse, normalize_date, parse_parts, Precision


def test_normalize():
    assert normalize_date(None) is None
    assert normalize_date("2001") == "2001"
    assert normalize_date(2001) == "2001"
    assert normalize_date(201) is None

    assert normalize_date("2001-01-") == "2001-01"
    assert normalize_date("2001-1") == "2001-01"
    assert normalize_date("2001-W19") == "2001"
    assert normalize_date("2001-05-18") == "2001-05-18"
    assert normalize_date("2001-02-31") is None
    assert normalize_date("2001-05-18", Precision.YEAR) == "2001"
    text = "2021-07-01T13:43:22.175889+00:00"
    assert normalize_date(text, Precision.MINUTE) == "2021-07-01T13:43"
    text = "2021-07-01T13:43:22.175889+06:00"
    assert normalize_date(text, Precision.MINUTE) == "2021-07-01T07:43"
    text = "2021-07-01T13:43:22.175889-08:45"
    assert normalize_date(text, Precision.MINUTE) == "2021-07-01T22:28"

    now = datetime.utcnow().astimezone(timezone.utc)
    assert parse(now).dt == now
    assert parse(now.date()).text == now.date().isoformat()
    assert str(parse(2001)) == "2001"
    assert repr(parse(2001)) == "<DatePrefix('2001', %r)>" % Precision.YEAR

    # feed a prefix to parse:
    prefix = parse(now)
    out = parse(prefix)
    assert out == prefix


def test_parse_parts():
    assert parse_parts(year=None).text is None
    assert parse_parts(year=2001, month=3, day=0).text == "2001-03"
    assert parse_parts(year=2001, month="03", day="0").text == "2001-03"
