import re
from datetime import datetime, date, timedelta, timezone

from prefixdate.precision import Precision

REGEX = re.compile(
    r"^((?P<year>[12]\d{3})"
    r"(-(?P<month>[01]?[0-9])"
    r"(-(?P<day>[0123]?[0-9])"
    r"([T ]"
    r"((?P<hour>[012]?\d)"
    r"(:(?P<minute>\d{1,2})"
    r"(:(?P<second>\d{1,2})"
    r"(\.\d{6})?"
    r"(Z|(?P<tzsign>[-+])(?P<tzhour>\d{2})(:?(?P<tzminute>\d{2}))"
    r"?)?)?)?)?)?)?)?)?.*"
)


class DatePrefix(object):
    """A date that is specified in terms of a value and an additional precision,
    which defines how well specified the date is. A datetime representation is
    provided, but it is not aware of the precision aspect."""

    __slots__ = ["precision", "dt", "text"]

    def __init__(self, raw, precision=Precision.FULL):
        self.precision = precision
        self.dt = self._parse(raw)
        if self.dt is None or self.precision == Precision.EMPTY:
            self.text = None
        else:
            utc_dt = self.dt.astimezone(timezone.utc)
            self.text = utc_dt.isoformat()[: self.precision.value]

    def _parse(self, raw):
        try:
            match = REGEX.match(raw)
        except TypeError:
            if isinstance(raw, datetime):
                return raw
            if isinstance(raw, date):
                return self._parse(raw.isoformat())
            if isinstance(raw, int):
                if 1000 < raw < 9999:
                    return self._parse(str(raw))
            return None
        year = self._extract(match, "year", Precision.EMPTY)
        month = self._extract(match, "month", Precision.YEAR)
        day = self._extract(match, "day", Precision.MONTH)
        hour = self._extract(match, "hour", Precision.DAY)
        minute = self._extract(match, "minute", Precision.HOUR)
        second = self._extract(match, "second", Precision.DAY)
        try:
            return datetime(
                year or 1000,
                month or 1,
                day or 1,
                hour or 0,
                minute or 0,
                second or 0,
                tzinfo=self._tzinfo(match),
            )
        except ValueError:
            return None

    def _extract(self, match, group, precision):
        try:
            value = int(match.group(group))
            if value > 0:
                return value
        except (ValueError, TypeError, AttributeError):
            pass
        pval = min(self.precision.value, precision.value)
        self.precision = Precision(pval)

    def _tzinfo(self, match):
        """Parse the time zone information from a datetime string."""
        # This is probably a bit rough-and-ready, there are good libraries
        # for this. Do we want to depend on one of them?
        try:
            sign = -1 if match.group("tzsign") == "-" else 1
            hours = sign * int(match.group("tzhour"))
            minutes = sign * int(match.group("tzminute"))
            delta = timedelta(hours=hours, minutes=minutes)
            return timezone(delta)
        except (ValueError, TypeError, AttributeError):
            pass
        return timezone.utc

    def __str__(self):
        return self.text

    def __repr__(self):
        return "<DatePrefix(%r, %r)>" % (self.text, self.precision)
