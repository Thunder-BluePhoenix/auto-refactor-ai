# Changelog

All notable changes to Auto Refactor AI will be documented in this file.

## [V3] - 2025-12-08

### Added
- **Pip Installable Package**
  - Proper `pyproject.toml` configuration for packaging
  - Console script entry point: `auto-refactor-ai` command
  - Users can now run `auto-refactor-ai` instead of `python -m auto_refactor_ai`
  - Package can be installed with `pip install auto-refactor-ai`

- **Package Distribution**
  - Built distributions: wheel (.whl) and source (.tar.gz)
  - `MANIFEST.in` for controlling distributed files
  - MIT `LICENSE` file
  - Development dependencies in `[project.optional-dependencies]`

- **Installation Tools**
  - `scripts/verify_install.py` - Comprehensive installation verification
  - Development mode installation: `pip install -e .`
  - Build tools integration with `python -m build`

- **Documentation**
  - `docs/versions/V1_GUIDE.md` - Complete V1 implementation guide
  - `docs/versions/V2_GUIDE.md` - Complete V2 implementation guide
  - `docs/versions/V3_GUIDE.md` - Complete V3 implementation guide
  - Updated package metadata and classifiers

### Changed
- Updated version to 0.3.0
- CLI description updated to specify V2 features (will update to V3 in next iteration)
- Package structure reorganized for distribution
- Entry point changed from `auto_refactor_ai:main` to `auto_refactor_ai.cli:main`
- Development status classifier: "4 - Beta"

### Testing
- Comprehensive 6-test verification suite
- Tests for imports, command availability, file analysis, JSON output, config loading, CLI args
- All tests pass successfully
- Package installs correctly in development mode

### Learning Outcomes
- Python packaging with `pyproject.toml`
- Console script entry points
- Package distribution (wheel vs source)
- Semantic versioning
- Build system configuration
- Installation verification
- Package metadata and classifiers

---

## [V2] - 2025-12-07

### Added
- **Configuration File Support**
  - Auto-discovery of config files in current and parent directories
  - Support for `.auto-refactor-ai.toml` format
  - Support for `.auto-refactor-ai.yaml` / `.auto-refactor-ai.yml` formats
  - Integration with `pyproject.toml` under `[tool.auto-refactor-ai]` section
  - Command-line arguments override config file settings
  - New `--config` flag to specify custom config file path

- **JSON Output Mode**
  - New `--format` flag with `text` (default) and `json` options
  - Machine-readable JSON output includes:
    - Configuration settings used
    - Summary statistics (total, critical, warn, info counts)
    - Detailed issue list with all metadata
  - Perfect for IDE integration and CI/CD pipelines

- **Enhanced Architecture**
  - New `config.py` module for configuration management
  - `to_dict()` method on `Issue` class for JSON serialization
  - `Config` dataclass for type-safe configuration
  - Fallback TOML/YAML parsers for Python < 3.11 compatibility

- **Example Configurations**
  - `examples/config-strict.toml` - High quality standards
  - `examples/config-relaxed.toml` - Lenient for legacy code
  - `examples/.auto-refactor-ai.yaml` - YAML format example

### Changed
- CLI now loads configuration from files by default
- Updated CLI description to "V2"
- Help text updated to reflect config file options

### Learning Outcomes
- Configuration management patterns
- TOML and YAML parsing
- JSON serialization and data modeling
- CLI argument precedence (config file < CLI args)

---

## [V1] - 2025-12-07

### Added
- **Multiple Analysis Rules**
  - Rule 2: Too many parameters detection
  - Rule 3: Deep nesting detection
  - `--max-params` CLI flag (default: 5)
  - `--max-nesting` CLI flag (default: 3)

- **Severity Levels**
  - `Severity` enum with INFO, WARN, CRITICAL levels
  - Dynamic severity assignment based on threshold violations:
    - INFO: 1-1.5x over limit
    - WARN: 1.5-2x over limit
    - CRITICAL: 2x+ over limit

- **Enhanced Output**
  - Issues sorted by severity (CRITICAL → WARN → INFO)
  - Summary table showing counts by severity
  - Cleaner, more professional output format

- **Improved Architecture**
  - `Issue` dataclass replacing `FunctionIssue`
  - Rule-based plugin architecture (easy to add new rules)
  - `NestingVisitor` class using AST visitor pattern
  - Separate functions for each rule check

- **Comprehensive Test Suite**
  - `test_files/` directory with organized test cases
  - `test_perfect_code.py` - Examples of good code
  - `test_length_issues.py` - Function length tests
  - `test_parameter_issues.py` - Parameter count tests
  - `test_nesting_issues.py` - Nesting depth tests
  - `test_combined_issues.py` - Multiple violations
  - `test_edge_cases.py` - Edge cases and special scenarios
  - Test files README with detailed documentation

### Changed
- Renamed `FunctionIssue` to `Issue` (more generic)
- `analyze_file()` now returns `List[Issue]` instead of `List[FunctionIssue]`
- CLI output now shows severity levels in brackets
- Directory analysis now shows summary table

### Learning Outcomes
- AST visitor pattern for code analysis
- Enums and dataclasses in Python
- Software architecture (rule-based design)
- More advanced AST manipulation
- Code quality theory (complexity, cohesion)

---

## [V0] - 2025-12-07

### Added
- **Core Functionality**
  - Basic CLI with `argparse`
  - Single rule: Function length detection
  - `--max-len` CLI flag (default: 30 lines)
  - File and directory scanning support
  - Human-readable text output

- **Project Structure**
  - `auto_refactor_ai/` package
  - `analyzer.py` - Core analysis logic
  - `cli.py` - Command-line interface
  - `__init__.py` and `__main__.py` for package structure

- **Basic Infrastructure**
  - `pyproject.toml` for package metadata
  - Initial README with documentation
  - Sample test files

- **Analysis Features**
  - Parse Python files using `ast` module
  - Detect functions exceeding line length threshold
  - Provide actionable refactoring suggestions
  - Recursive directory scanning for `.py` files

### Learning Outcomes
- Python AST (Abstract Syntax Tree) basics
- Building CLI tools with argparse
- Python packaging structure
- Working with pathlib for file operations
- Basic code analysis concepts

---

## Future Versions (Planned)

### V3 - Pip Installable Package
- Proper package distribution setup
- Upload to TestPyPI / PyPI
- Console script entry point
- Installation via `pip install auto-refactor-ai`

### V4 - Tests & CI/CD
- Unit tests with pytest
- Test coverage reporting
- GitHub Actions workflow
- Pre-commit hooks
- Linting and formatting

### V5 - Detailed Explanations
- Natural language explanations for each issue
- Refactoring theory and best practices
- Example code snippets
- Educational mode

### V6 - AI-Powered Suggestions
- LLM integration (OpenAI, Anthropic, etc.)
- Generate refactored code suggestions
- Context-aware recommendations
- `--ai-suggestions` flag

### V7 - Auto-Refactor Mode
- Generate and apply code patches
- Diff generation with unified format
- Safe backup and rollback
- `--apply` flag with safety checks

### V8 - Project-Level Analysis
- Detect duplicate code across files
- Suggest shared helper modules
- Code similarity detection
- Architectural recommendations

### V9 - Git Integration
- Pre-commit hook support
- Analyze only changed files
- Git diff integration
- Block commits on severe issues

### V10 - Refactor Planning
- High-level refactor roadmaps
- Prioritized issue lists
- Complexity analysis
- `--plan` mode

### V11 - Editor Integration
- VS Code extension
- Neovim/Vim plugin
- JetBrains IDE support
- LSP (Language Server Protocol)

### V12 - Community Release
- Comprehensive documentation
- Contributor guidelines
- Issue templates
- Community building
- Marketing and promotion
