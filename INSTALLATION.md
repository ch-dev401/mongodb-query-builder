# Installation & Publishing Guide

## For Users

### Installing from PyPI (Once Published)

```bash
# Basic installation
pip install mongodb-query-builder

# With MongoDB support
pip install mongodb-query-builder[mongodb]

# With async support
pip install mongodb-query-builder[async]

# With all optional dependencies
pip install mongodb-query-builder[all]
```

### Installing from Source

```bash
# Clone the repository
git clone https://github.com/ch-dev401/mongodb-query-builder.git
cd mongodb-query-builder

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev,test]"
```

## For Developers

### Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ch-dev401/mongodb-query-builder.git
   cd mongodb-query-builder
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   make install-dev
   # Or manually:
   pip install -e ".[dev,test]"
   ```

### Development Workflow

```bash
# Format code
make format

# Run linters
make lint

# Run tests
make test

# Run tests with coverage
make test-cov

# Clean build artifacts
make clean
```

## Publishing to PyPI

### Prerequisites

1. **Install build tools:**
   ```bash
   pip install build twine
   ```

2. **Create PyPI account:**
   - Register at https://pypi.org/account/register/
   - Register at https://test.pypi.org/account/register/ (for testing)

3. **Create API tokens:**
   - Go to Account Settings → API tokens
   - Create tokens for both PyPI and TestPyPI

### Building the Package

```bash
# Clean previous builds
make clean

# Build distribution packages
make build
# This creates:
# - dist/mongodb_query_builder-0.1.0.tar.gz (source distribution)
# - dist/mongodb_query_builder-0.1.0-py3-none-any.whl (wheel)
```

### Testing on TestPyPI

1. **Upload to TestPyPI:**
   ```bash
   make upload-test
   # Or manually:
   python -m twine upload --repository testpypi dist/*
   ```

2. **Test installation from TestPyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ mongodb-query-builder
   ```

3. **Verify it works:**
   ```python
   from mongodb_query_builder import QueryFilter
   q = QueryFilter().field("test").equals("value")
   print(q.build())  # Should print: {'test': 'value'}
   ```

### Publishing to PyPI

1. **Update version in `src/mongodb_query_builder/__version__.py`**

2. **Update CHANGELOG.md** with release notes

3. **Build and upload:**
   ```bash
   make upload
   # Or manually:
   python -m twine upload dist/*
   ```

4. **Create a GitHub release:**
   - Tag: `v0.1.0`
   - Title: `v0.1.0 - Initial Release`
   - Description: Copy from CHANGELOG.md

5. **Verify installation:**
   ```bash
   pip install mongodb-query-builder
   ```

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Backwards-compatible functionality
- **PATCH** version: Backwards-compatible bug fixes

### Pre-release Versions

- Alpha: `0.1.0a1`, `0.1.0a2`
- Beta: `0.1.0b1`, `0.1.0b2`
- Release Candidate: `0.1.0rc1`, `0.1.0rc2`

## Checklist Before Publishing

- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Linters pass (`make lint`)
- [ ] Version updated in `__version__.py`
- [ ] CHANGELOG.md updated
- [ ] README.md is current
- [ ] Documentation is up to date
- [ ] Tested on TestPyPI
- [ ] All optional dependencies work
- [ ] LICENSE is correct
- [ ] GitHub repository is public (if applicable)

## Troubleshooting

### Build Issues

**Problem:** Build fails with "No module named 'setuptools'"
```bash
pip install --upgrade setuptools wheel build
```

**Problem:** "version conflict" during build
```bash
make clean
pip install --upgrade pip setuptools wheel
make build
```

### Upload Issues

**Problem:** "Invalid or non-existent authentication"
- Create API token in PyPI settings
- Use token as password (username: `__token__`)

**Problem:** "File already exists"
- Version already published
- Increment version number
- Clean and rebuild: `make clean && make build`

### Installation Issues

**Problem:** "Could not find a version"
- Check package name spelling
- Verify package is published
- Check PyPI.org for package status

**Problem:** Import errors after installation
```bash
pip install --force-reinstall mongodb-query-builder
```

## Continuous Deployment

For automated publishing with GitHub Actions, see `.github/workflows/publish.yml` (to be created in Option 5).

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Setuptools Documentation](https://setuptools.pypa.io/)