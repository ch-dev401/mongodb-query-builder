# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-12

### Added
- **Declarative Search Models**: New `SearchModel` class for defining Atlas Search schemas
  - `IndexField`: Configure field-level search and facet settings
  - `SearchQuery`: Type-safe query builder with automatic field validation
  - Support for complex field names with dot notation via `fields` dictionary
  - Automatic validation of search operations against field configurations
  - Comprehensive API documentation and examples

### Changed
- Updated package exports to include new search model classes
- Enhanced test coverage to 89.20% overall (98% for search models module)

### Fixed
- Improved Makefile Windows compatibility for clean commands

## [1.0.2] - 2025-12-XX

### Added
- Version checking and updating scripts
- Improved version management workflow

### Changed
- Documentation improvements

## [1.0.1] - 2025-12-XX

### Fixed
- README documentation links
- Project configuration updates

## [1.0.0] - 2025-12-XX

### Added
- Initial release
- QueryFilter for building MongoDB query filters
- AggregateBuilder for constructing aggregation pipelines
- AtlasSearchBuilder for creating Atlas Search queries
- CompoundBuilder for complex compound search queries
- Comprehensive test suite
- Full API documentation
- Type hints throughout

[1.1.0]: https://github.com/ch-dev401/mongodb-query-builder/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/ch-dev401/mongodb-query-builder/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/ch-dev401/mongodb-query-builder/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/ch-dev401/mongodb-query-builder/releases/tag/v1.0.0
