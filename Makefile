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
	-@if exist build rd /s /q build 2>nul
	-@if exist dist rd /s /q dist 2>nul
	-@if exist .eggs rd /s /q .eggs 2>nul
	-@for /d /r %%i in (*.egg-info) do @echo %%i | findstr /i /v "\\venv\\" | findstr /i /v "\\.venv\\" | findstr /i /v "\\env\\" > nul && if exist "%%i" rd /s /q "%%i" 2>nul
	-@for /r %%i in (*.egg) do @echo %%i | findstr /i /v "\\venv\\" | findstr /i /v "\\.venv\\" | findstr /i /v "\\env\\" > nul && if exist "%%i" del /f /q "%%i" 2>nul

clean-pyc:
	-@for /r %%i in (*.pyc) do @echo %%i | findstr /i /v "\\venv\\" | findstr /i /v "\\.venv\\" | findstr /i /v "\\env\\" > nul && if exist "%%i" del /f /q "%%i" 2>nul
	-@for /r %%i in (*.pyo) do @echo %%i | findstr /i /v "\\venv\\" | findstr /i /v "\\.venv\\" | findstr /i /v "\\env\\" > nul && if exist "%%i" del /f /q "%%i" 2>nul
	-@for /r %%i in (*~) do @echo %%i | findstr /i /v "\\venv\\" | findstr /i /v "\\.venv\\" | findstr /i /v "\\env\\" > nul && if exist "%%i" del /f /q "%%i" 2>nul
	-@for /d /r %%i in (__pycache__) do @echo %%i | findstr /i /v "\\venv\\" | findstr /i /v "\\.venv\\" | findstr /i /v "\\env\\" > nul && if exist "%%i" rd /s /q "%%i" 2>nul
	-@for /d /r %%i in (.pytest_cache) do @echo %%i | findstr /i /v "\\venv\\" | findstr /i /v "\\.venv\\" | findstr /i /v "\\env\\" > nul && if exist "%%i" rd /s /q "%%i" 2>nul
	-@for /d /r %%i in (.mypy_cache) do @echo %%i | findstr /i /v "\\venv\\" | findstr /i /v "\\.venv\\" | findstr /i /v "\\env\\" > nul && if exist "%%i" rd /s /q "%%i" 2>nul
	-@if exist .coverage del /f /q .coverage 2>nul
	-@if exist htmlcov rd /s /q htmlcov 2>nul


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
