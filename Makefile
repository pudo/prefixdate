
test:
	mypy --strict prefixdate
	pytest --cov-report html --cov-report term --cov=prefixdate tests/