.PHONY: install format lint clean test pytest mypy docs docs-serve

install:
	uv sync
	pre-commit install

lint:
	uv run ruff check --fix ./levelup/
	uv run ruff format ./levelup/
	uv run mypy ./levelup/

mypy:
	uv run mypy ./levelup/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf site/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	uv run pytest

pytest:
	uv run pytest

docs:
	uv run mkdocs build

docs-serve:
	uv run mkdocs serve
