import re
import logging
from typing import cast, Union, Optional, Match, Tuple
from datetime import datetime, date, timedelta, timezone

from prefixdate.precision import Precision

log = logging.getLogger(__name__)

Raw = Union[None, str, date, datetime, int, "DatePrefix"]

REGEX = re.compile(
    r"^((?P<year>[12]\d{3})"
    r"(-(?P<month>\d{1,2})"
    r"(-(?P<day>\d{1,2})"
    r"([T ]"
    r"((?P<hour>\d{1,2})"
    r"(:(?P<minute>\d{1,2})"
    r"(:(?P<second>\d{1,2})"
    r"(\.\d{4,6})?"
    r"(Z|(?P<tzsign>[-+])(?P<tzhour>\d{2})(:?(?P<tzminute>\d{2}))"
    r"?)?)?)?)?)?)?)?)?.*"
)


class DatePrefix(object):
    """A date that is specified in terms of a value and an additional precision,
    which defines how well specified the date is. A datetime representation is
    provided, but it is not aware of the precision aspect."""

    __slots__ = ["precision", "dt", "text"]

    def __init__(self, raw: Raw, precision: Precision = Precision.FULL):
        self.precision, self.dt = self._parse(raw, precision)
        self.text: Optional[str] = None
        if self.dt is not None and self.precision != Precision.EMPTY:
            dt = self.dt
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            self.text = dt.isoformat()[: self.precision.value]

    def _parse(
        self, raw: Raw, precision: Precision
    ) -> Tuple[Precision, Optional[datetime]]:
        try:
            match = cast(Match[str], REGEX.match(raw))  # type: ignore
        except TypeError:
            if isinstance(raw, datetime):
                return (precision, raw)
            if isinstance(raw, date):
                return self._parse(raw.isoformat(), precision)
            if isinstance(raw, int):
                if 1000 < raw < 9999:
                    return self._parse(str(raw), Precision.YEAR)
            if isinstance(raw, DatePrefix):
                return (raw.precision, raw.dt)
            log.warning("Date value is invalid: %s", raw)
            return (Precision.EMPTY, None)
        precision, year = self._extract(match, "year", precision, Precision.EMPTY)
        precision, month = self._extract(match, "month", precision, Precision.YEAR)
        precision, day = self._extract(match, "day", precision, Precision.MONTH)
        precision, hour = self._extract(match, "hour", precision, Precision.DAY)
        precision, minute = self._extract(match, "minute", precision, Precision.HOUR)
        precision, second = self._extract(match, "second", precision, Precision.MINUTE)
        try:
            dt = datetime(
                year or 1000,
                month or 1,
                day or 1,
                hour or 0,
                minute or 0,
                second or 0,
                tzinfo=self._tzinfo(match),
            )
            return (precision, dt)
        except ValueError:
            log.warning("Date string is invalid: %s", raw)
            return (Precision.EMPTY, None)

    def _extract(
        self, match: Match[str], group: str, precision: Precision, fail: Precision
    ) -> Tuple[Precision, Optional[int]]:
        try:
            value = int(match.group(group))
            if value > 0:
                return (precision, value)
        except (ValueError, TypeError, AttributeError):
            pass
        pval = min(precision.value, fail.value)
        return (Precision(pval), None)

    def _tzinfo(self, match: Match[str]) -> Optional[timezone]:
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
        return None

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        return self.text or ""

    def __repr__(self) -> str:
        return "<DatePrefix(%r, %r)>" % (self.text, self.precision)
