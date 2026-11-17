PYTHON ?= python

.PHONY: lint type test migrate rehearsal rehearsal-start rehearsal-stop rehearsal-smoke

lint:
	$(PYTHON) -m ruff check --config pyproject.toml engine api

type:
	$(PYTHON) -m mypy --config-file pyproject.toml engine api

test:
	$(PYTHON) -m pytest -c pyproject.toml tests engine/tests api/tests

migrate:
	$(PYTHON) -m alembic upgrade head

rehearsal:
	$(PYTHON) scripts/rehearsal.py

rehearsal-start:
	$(PYTHON) scripts/rehearsal_start.py

rehearsal-stop:
	docker compose down

rehearsal-smoke:
	$(PYTHON) scripts/rehearsal_smoke.py
