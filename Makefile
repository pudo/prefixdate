.PHONY: lint typecheck test

lint:
	ruff check prefixdate tests

typecheck:
	mypy --strict prefixdate

test: lint typecheck
	pytest --cov-report html --cov-report term --cov=prefixdate tests/