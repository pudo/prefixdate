# Prefix date parser

This is a helper class to parse dates with varied degrees of precision. For
example, a data source might state a date as `2001`, `2001-4` or `2001-04-02`,
with the implication that only the year, month or day is known. This library
will process such partial dates into a structured format and allow their
validation and re-formatting (e.g. turning `2001-4` into `2001-04` above).

The library does not support the complexities of the ISO 8601 and RFC 3339
standards including date ranges and calendar-week/day-of-year notations.

## Installation

Install `prefixdate` using PyPI:

```bash
$ pip install prefixdate
```

## Usage

The library provides a variety of helper functions to parse and format
partial dates:

```python
from prefixdate import parse, normalize_date, Precision

# Parse returns a `DatePrefix` object:
date = parse('2001-3')
assert date.text == '2001-03'
date = parse(2001)
assert date.text == '2001'
assert date.precision == Precision.YEAR

# Normalize to a standard string:
assert normalize_date('2001-1') == '2001-01'
assert normalize_date('2001-00-00') == '2001'
assert normalize_date('Boo!') is None

# This also works for datetimes:
from datetime import datetime
now = datetime.utcnow().isoformat()
minute = normalize_date(now, precision=Precision.MINUTE)

# You can also feed in None, date and datetime:
normalize_date(datetime.utcnow())
normalize_date(datetime.date())
normalize_date(None)
```

## Caveats

* Does not process milliseconds yet.
* Does not process invalid dates, like Feb 31st.
