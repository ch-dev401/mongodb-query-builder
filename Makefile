.PHONY: help install install-dev install-test clean clean-build clean-pyc lint format test test-cov build upload-test upload docs

help:
	@echo "MongoDB Query Builder - Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install          Install package in editable mode"
	@echo "  make install-dev      Install with development dependencies"
	@echo "  make install-test     Install with testing dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make format           Format code with black and isort"
	@echo "  make lint             Run linters (flake8, pylint, mypy)"
	@echo "  make test             Run tests with pytest"
	@echo "  make test-cov         Run tests with coverage report"
	@echo ""
	@echo "Building:"
	@echo "  make build            Build distribution packages"
	@echo "  make clean            Remove build artifacts"
	@echo "  make clean-build      Remove build artifacts only"
	@echo "  make clean-pyc        Remove Python cache files"
	@echo ""
	@echo "Publishing:"
	@echo "  make upload-test      Upload to TestPyPI"
	@echo "  make upload           Upload to PyPI"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs             Build Sphinx documentation"
	@echo "  make mkdocs-serve     Serve MkDocs locally (port 8000)"
	@echo "  make mkdocs-build     Build MkDocs site"
	@echo "  make mkdocs-deploy    Deploy MkDocs with mike (versioning)"
	@echo ""
	@echo "Version Management:"
	@echo "  make version VERSION=X.Y.Z    Update version in all files"
	@echo "  make version-check            Show current version"
	@echo "  make release VERSION=X.Y.Z    Update version, build, and tag"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test]"

install-test:
	pip install -e ".[test]"

clean: clean-build clean-pyc

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '.mypy_cache' -exec rm -rf {} +
	rm -f .coverage
	rm -rf htmlcov/

format:
	black src tests
	isort src tests

lint:
	flake8 src tests
	pylint src
	mypy src

test:
	pytest

test-cov:
	pytest --cov=mongodb_query_builder --cov-report=html --cov-report=term

build: clean
	python -m build

upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

docs:
	cd docs && make html

mkdocs-serve:
	mkdocs serve

mkdocs-build:
	mkdocs build

mkdocs-deploy:
	mike deploy --push --update-aliases $(VERSION) latest

version:
	@python scripts/update_version.py $(VERSION)

version-check:
	@python scripts/check_version.py

release: version build
	@echo "Creating git tag v$(VERSION)..."
	@git add -A
	@git commit -m "Release version $(VERSION)"
	@git tag -a v$(VERSION) -m "Release version $(VERSION)"
	@echo ""
	@echo "Release prepared! Next steps:"
	@echo "  1. Review changes: git show"
	@echo "  2. Push to remote: git push origin main --tags"
	@echo "  3. Upload to PyPI: make upload"

# Shortcut aliases
fmt: format
l: lint
t: test
tc: test-cov
b: build
