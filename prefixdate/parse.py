import re
import logging
from functools import total_ordering
from typing import cast, Union, Optional, Match, Tuple
from datetime import datetime, date, timedelta, timezone

from prefixdate.precision import Precision

log = logging.getLogger(__name__)

Raw = Union[None, str, date, datetime, int, "DatePrefix"]

REGEX = re.compile(
    r"^\s*((?P<year>[12]\d{3}\b)"
    r"(-(?P<month>\d{1,2}\b)"
    r"(-(?P<day>\d{1,2})"
    r"([T ]"
    r"((?P<hour>\d{1,2}\b)"
    r"(:(?P<minute>\d{1,2}\b)"
    r"(:(?P<second>\d{1,2}\b)"
    r"(\.\d{4,6}\b)?"
    r"(Z|(?P<tzsign>[-+])(?P<tzhour>\d{2})(:?(?P<tzminute>\d{2}\b))"
    r"?)?)?)?)?)?)?)?)?.*"
)


@total_ordering
class DatePrefix(object):
    """A date that is specified in terms of a value and an additional precision,
    which defines how well specified the date is. A datetime representation is
    provided, but it is not aware of the precision aspect."""

    __slots__ = ["precision", "dt", "text"]

    def __init__(self, raw: Raw, precision: Precision = Precision.FULL):
        self.precision, self.dt = self._parse(raw, precision)
        self.text: Optional[str] = None
        if self.dt is not None and self.precision != Precision.EMPTY:
            self.dt = self.dt
            if self.dt.tzinfo is not None and self.dt.tzinfo != timezone.utc:
                self.dt = self.dt.astimezone(timezone.utc)
            self.text = self.dt.isoformat()[: self.precision.value]

    def _parse(self, raw: Raw, pcn: Precision) -> Tuple[Precision, Optional[datetime]]:
        try:
            match = cast(Match[str], REGEX.match(raw))  # type: ignore
        except TypeError:
            if isinstance(raw, datetime):
                return (pcn, raw)
            if isinstance(raw, date):
                return self._parse(raw.isoformat(), pcn)
            if isinstance(raw, int):
                if 1000 < raw < 9999:
                    return self._parse(str(raw), Precision.YEAR)
            if isinstance(raw, DatePrefix):
                return (raw.precision, raw.dt)
            if raw is not None:
                log.warning("Date value is invalid: %s", raw)
            return (Precision.EMPTY, None)
        pcn, year = self._extract(match, "year", 1000, pcn, Precision.EMPTY)
        pcn, month = self._extract(match, "month", 1, pcn, Precision.YEAR)
        pcn, day = self._extract(match, "day", 1, pcn, Precision.MONTH)
        pcn, hour = self._extract(match, "hour", 0, pcn, Precision.DAY)
        pcn, minute = self._extract(match, "minute", 0, pcn, Precision.HOUR)
        pcn, second = self._extract(match, "second", 0, pcn, Precision.MINUTE)
        try:
            tz = self._tzinfo(match)
            dt = datetime(year, month, day, hour, minute, second, tzinfo=tz)
            return (pcn, dt)
        except ValueError:
            log.warning("Date string is invalid: %s", raw)
            return (Precision.EMPTY, None)

    def _extract(
        self,
        match: Match[str],
        group: str,
        lowest: int,
        pcn: Precision,
        fail: Precision,
    ) -> Tuple[Precision, int]:
        try:
            value = int(match.group(group))
            if value >= lowest:
                return (pcn, value)
        except (ValueError, TypeError, AttributeError):
            pass
        precision = Precision(min(pcn.value, fail.value))
        return (precision, lowest)

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

    def __lt__(self, other: object) -> bool:
        # cf. https://docs.python.org/3/library/functools.html#functools.total_ordering
        if isinstance(other, DatePrefix):
            return str(self) < str(other)
        return NotImplemented

    def __str__(self) -> str:
        return self.text or ""

    def __repr__(self) -> str:
        return "<DatePrefix(%r, %r)>" % (self.text, self.precision)

    def __hash__(self) -> int:
        return hash(repr(self))
