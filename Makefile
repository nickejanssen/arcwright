PYTHON ?= python

.PHONY: lint type test migrate

lint:
	$(PYTHON) -m ruff check --config pyproject.toml engine api

type:
	$(PYTHON) -m mypy --config-file pyproject.toml engine api

test:
	$(PYTHON) -c "import sys, pytest; code = pytest.main(['-c', 'pyproject.toml', 'tests']); sys.exit(0 if code == 5 else code)"

migrate:
	$(PYTHON) -m alembic upgrade head
