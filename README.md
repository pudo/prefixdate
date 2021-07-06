# Prefix date parser

This is a helper class to parse dates with varied degrees of precision. For
example, a data source might state a date as `2001`, `2001-4` or `2001-04-02`,
with the implication that only the year, month or day is known. This library
will process such partial dates into a structured format and allow their
validation and re-formatting (e.g. turning `2001-4` into `2001-04` above).

The library does not support the complexities of the ISO 8601 and RFC 3339
standards including date ranges and calendar-week/day-of-year notations.

## Installation
