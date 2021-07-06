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

date = parse(None)
assert date.text is None
assert date.precision == Precision.EMPTY
# This will also be the outcome for invalid dates!

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

You can also use the `parse_parts` helper, which is similar to the constructor
for a `datetime`:

```python
from prefixdate import parse_parts, Precision

date = parse_parts(2001, '3', None)
assert date.precision == Precision.MONTH
assert date.text == '2001-03'
```

### Format strings

For dates which are not already stored in an ISO 8601-like string format, you
can supply one or many format strings for `datetime.strptime`. The format strings
will be analysed to determine how precise the resulting dates are expected to be.

```python 
from prefixdate import parse_format, parse_formats, Precision

date = parse_format('YEAR 2021', 'YEAR %Y')
assert date.precision == Precision.YEAR
assert date.text == '2021'

# You can try out multiple formats in sequence. The first non-empty prefix
# will be returned:
date = parse_formats('2021', ['%Y-%m-%d', '%Y-%m', '%Y'])
assert date.precision == Precision.YEAR
assert date.text == '2021'
```

## Caveats

* Datetimes are always converted to UTC and made naive (tzinfo stripped)
* Does not process milliseconds yet.
* Does not process invalid dates, like Feb 31st.
