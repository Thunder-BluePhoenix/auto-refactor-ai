# Changelog

All notable changes to Auto Refactor AI will be documented in this file.

## [V11] - 2025-12-08

### Added
- **Language Server Protocol (LSP) Support**
  - New `lsp_server.py` module (270+ lines)
  - Real-time diagnostics as you type
  - Code actions for quick fixes
  - Hover information with explanations
  - Works with any LSP-compatible editor

- **New CLI Flags**
  - `--lsp` - Start LSP server (stdio transport)
  - `--lsp-tcp` - Use TCP transport for debugging
  - `--lsp-port` - Configure TCP port (default: 2087)

- **VS Code Extension**
  - `vscode-extension/` directory with full extension
  - Language client integration
  - Configuration options
  - Commands for manual analysis

- **New Optional Dependency**
  - `pip install auto-refactor-ai[lsp]` - Install with pygls

- **New Tests**
  - `tests/test_lsp_server.py` - 7 tests
  - Total test count: 290 (up from 289)

### Changed
- Updated version to 0.11.0
- CLI description updated to include LSP

### Example Usage
```bash
# Start LSP server (for editor integration)
auto-refactor-ai --lsp

# Start with TCP transport (for debugging)
auto-refactor-ai --lsp --lsp-tcp --lsp-port 3000
```

---

## [V10] - 2025-12-08

### Added
- **Refactor Plan Mode**
  - `--plan` flag generates strategic refactoring roadmaps
  - Priority-ranked issues with effort/impact analysis
  - Quick wins identification
  - Multi-phase roadmap generation

- **LLM Strategic Advice**
  - AI-powered recommendations integrated into plans
  - Use `--plan --ai-suggestions` for LLM insights
  - Customizable with `--ai-provider` and `--ai-model`

- **HTML Report Generation**
  - `--plan-format html` generates styled HTML reports
  - Dark theme with visual metrics grid
  - Responsive design for desktop viewing

- **Output File Support**
  - `--output` / `-o` flag to save reports to file
  - Works with text, markdown, and HTML formats

- **New Tests**
  - `tests/test_refactor_planner_v10.py` - 9 tests
  - Total test count: 289 (up from 280)

- **Mypy Type Fixes**
  - Fixed all 26 mypy type errors across the codebase
  - Updated python_version to 3.9 in mypy config

### Changed
- Updated version to 0.10.0
- CLI description updated to include refactoring plans
- Test coverage: 87% (from 80%)

### Example Usage
```bash
# Generate text plan
auto-refactor-ai . --plan

# Generate HTML report with AI advice
auto-refactor-ai . --plan --plan-format html --ai-suggestions -o report.html
```

---

## [V9] - 2025-12-08

### Added
- **Git Integration**
  - New `git_utils.py` module
  - `--git` flag to analyze modified files
  - `--staged` flag to analyze staged files
  - Pre-commit hooks support (`.pre-commit-hooks.yaml`)

- **New Tests**
  - `tests/test_git_utils.py` - 6 tests
  - Total test count: 157 (up from 151)

### Changed
- Updated version to 0.9.0
- CLI description updated to "V9"

### Documentation
- `docs/versions/V9_GUIDE.md` - Complete V9 guide

---

## [V8] - 2025-12-08

### Added
- **Project-Level Analysis**
  - New `project_analyzer.py` module (400+ lines)
  - Cross-file duplicate code detection
  - AST normalization and hashing
  - Architecture recommendations

- **Duplicate Detection**
  - AST-based structural comparison
  - Hash-based grouping
  - Potential savings calculation
  - Module consolidation suggestions

- **New CLI Flags**
  - `--project` / `-p` - Enable project-level analysis
  - `--find-duplicates` - Find duplicate code
  - `--similarity-threshold` - Similarity threshold (0.0-1.0)
  - `--min-lines` - Minimum lines to consider

- **New Tests**
  - `tests/test_project_analyzer.py` - 15 tests
  - Total test count: 146 (up from 131)

- **New Test Files**
  - `test_files/test_duplicates_a.py` - Duplicate patterns
  - `test_files/test_duplicates_b.py` - Companion duplicates

### Changed
- Updated version to 0.8.0
- CLI description updated to "V8"

### Documentation
- `docs/versions/V8_GUIDE.md` - Complete V8 guide

### Learning Outcomes
- AST normalization techniques
- Code similarity algorithms
- Cross-file analysis patterns

---

## [V7] - 2025-12-08

### Added
- **Auto-Refactor Mode**
  - New `auto_refactor.py` module (400+ lines) for applying AI suggestions
  - Automatic application of refactorings to files
  - Unified diff generation with `difflib`
  - Before/after change previews

- **Backup System**
  - Timestamped file backups before modification
  - Configurable backup directory
  - Rollback capability from backups

- **New CLI Flags**
  - `--apply` - Apply AI-suggested refactorings to files
  - `--dry-run` - Show what would be applied without making changes
  - `--interactive` - Ask for approval before each change (y/n/q prompts)
  - `--backup` - Enable backups (default: True)
  - `--no-backup` - Disable backup creation
  - `--backup-dir` - Directory for backups (default: `.auto-refactor-backup`)

- **New Tests**
  - `tests/test_auto_refactor.py` - 18 tests for auto-refactor module
  - Tests for diff generation, backup, apply, rollback, formatting
  - Total test count: 131 (up from 113)

### Changed
- Updated version to 0.7.0
- CLI description updated to "V7" with auto-apply feature
- Package description now mentions auto-apply

### Documentation
- `docs/versions/V7_GUIDE.md` - Complete V7 implementation guide
- `V7_COMPLETION_SUMMARY.md` - Summary of all V7 achievements

### Learning Outcomes
- Working with diffs using `difflib`
- Safe file modification patterns
- Backup/restore strategies
- Interactive CLI design
- Destructive action protection

---

## [V6] - 2025-12-08

### Added
- **LLM Provider Integration**
  - New `llm_providers.py` module with unified LLM abstraction
  - Support for OpenAI (GPT-4o, GPT-4o-mini, GPT-4-turbo)
  - Support for Anthropic (Claude 3 Opus, Sonnet, Haiku)
  - Support for Google (Gemini 1.5 Pro, Flash)
  - Support for Ollama (local LLMs - CodeLlama, Llama2, Mistral)
  - Auto-detection of available providers via environment variables

- **AI-Powered Refactoring Suggestions**
  - New `ai_suggestions.py` module for generating code improvements
  - Extracts function source code from files
  - Sends to LLM with engineered prompts
  - Parses structured responses with before/after code
  - Calculates confidence scores
  - Tracks token usage and cost estimates

- **New CLI Flags**
  - `--ai-suggestions` - Get AI-powered refactoring suggestions
  - `--ai-provider` - Choose specific LLM provider (openai/anthropic/google/ollama)
  - `--ai-model` - Specify model (e.g., gpt-4o-mini, claude-3-haiku-20240307)
  - `--ai-max-issues` - Limit number of issues to analyze (default: 5)
  - `--check-providers` - Check which LLM providers are available

- **Prompt Engineering**
  - System prompt for code refactoring role
  - Structured user prompts with context
  - Response parsing for code blocks and explanations
  - Change summary extraction

- **Optional Dependencies**
  - `[ai]` - OpenAI support
  - `[ai-anthropic]` - Anthropic/Claude support
  - `[ai-google]` - Google Gemini support
  - `[ai-all]` - All providers

- **New Tests**
  - `tests/test_llm_providers.py` - 26 tests for LLM integration
  - `tests/test_ai_suggestions.py` - 15 tests for AI suggestions
  - Total test count: 113 (up from 75)

### Changed
- Updated version to 0.6.0
- CLI description updated to "V6" with AI-powered suggestions
- Package description now mentions LLM-based refactoring
- Added "ai", "llm", "gpt" to package keywords

### Documentation
- `docs/versions/V6_GUIDE.md` - Complete V6 implementation guide
- Updated installation instructions for AI dependencies
- API key configuration guide
- Cost estimation documentation

### Learning Outcomes
- Calling LLMs from Python (OpenAI, Anthropic, Google APIs)
- Prompt engineering for code refactoring
- API error handling and timeouts
- Token management and cost estimation
- Provider abstraction with factory pattern

---

## [V5] - 2025-12-08

### Added
- **Detailed Explanations System**
  - New `explanations.py` module (374 lines) with comprehensive explanation templates
  - `Explanation` dataclass with structured fields for why/how/examples
  - Pre-defined explanations for all 3 rules with educational content

- **New CLI Flags**
  - `--explain` flag for detailed explanations with full examples
  - `--explain-summary` flag for brief explanations (quick tips)
  - Severity-specific guidance for CRITICAL/WARN/INFO issues

- **Educational Content**
  - "Why it matters" sections explaining the impact of each issue
  - "How to fix" step-by-step guidance (5 steps per rule)
  - Good vs Bad code examples for each rule
  - References to Clean Code, Refactoring Guru, and design patterns

- **Rule Explanations**
  - **Function Too Long**: SRP, Extract Method, cognitive overload
  - **Too Many Parameters**: Parameter Object, Builder Pattern
  - **Deep Nesting**: Guard clauses, early returns, Strategy Pattern

- **New Tests**
  - `tests/test_explanations.py` with 15 comprehensive tests
  - Tests for getting explanations, formatting, severity guidance
  - Quality validation tests for explanation content
  - Total test count: 75 (up from 60)

### Changed
- Updated version to 0.5.0
- CLI description updated to "V5" with detailed explanations
- CLI now respects `--explain` and `--explain-summary` flags

### Documentation
- `docs/versions/V5_GUIDE.md` - Complete V5 implementation guide
- `V5_COMPLETION_SUMMARY.md` - Summary of all V5 achievements

### Learning Outcomes
- Good error message design principles
- Refactoring theory (DRY, SRP, cohesion)
- Documentation practices with examples
- Progressive disclosure (verbose vs summary)

---

## [V4] - 2025-12-08

### Added
- **Comprehensive Test Suite**
  - 60+ unit tests with pytest framework
  - Test coverage: 88% (exceeds 80% requirement)
  - Three test modules: `test_analyzer.py`, `test_config.py`, `test_cli.py`
  - 19 test classes covering all functionality
  - Edge case testing (syntax errors, empty files, invalid configs)

- **GitHub Actions CI/CD**
  - `.github/workflows/test.yml` - Automated testing pipeline
  - Tests run on 15 combinations (3 OS × 5 Python versions)
  - Multi-platform: Ubuntu, Windows, macOS
  - Python versions: 3.8, 3.9, 3.10, 3.11, 3.12
  - Code quality checks (black, ruff, mypy)
  - Self-analysis job (dogfooding)
  - Codecov integration for coverage tracking

- **Pre-commit Hooks**
  - `.pre-commit-config.yaml` - Automated quality checks
  - General file checks (trailing whitespace, EOF, YAML/TOML validation)
  - Black for code formatting (100-char line length)
  - Ruff for linting with auto-fixes
  - Mypy for static type checking
  - Self-analysis before commits (dogfooding with strict settings)
  - Pytest runs before every commit

- **Code Quality Tools Configuration**
  - Black configuration in `pyproject.toml` (100-char lines)
  - Ruff configuration (pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, flake8-bugbear)
  - Mypy configuration (type checking settings)
  - Coverage configuration (80% minimum, exclude test files)
  - All tools configured for Python 3.8+ compatibility

- **Development Dependencies**
  - `pytest>=7.0` - Test framework
  - `pytest-cov>=4.0` - Coverage reporting
  - `pytest-mock>=3.10` - Mocking utilities
  - `black>=23.0` - Code formatter
  - `ruff>=0.1.0` - Fast linter
  - `mypy>=1.0` - Type checker
  - `pre-commit>=3.0` - Pre-commit hooks framework

### Changed
- Updated version to 0.4.0
- Improved test isolation with proper setup/teardown
- Enhanced error handling in tests

### Testing Details
- **Analyzer Tests (26 tests)**
  - Severity enum and Issue dataclass tests
  - NestingVisitor AST pattern tests
  - Function length detection with all severity levels
  - Parameter count detection with *args, **kwargs
  - Nesting depth detection tests
  - Full file analysis integration tests
  - Edge cases: nonexistent files, syntax errors

- **Config Tests (22 tests)**
  - Config dataclass operations
  - TOML parsing (simple and pyproject.toml formats)
  - Config file discovery in parent directories
  - YAML parsing fallback
  - Auto-discovery integration

- **CLI Tests (12 tests)**
  - Text output formatting
  - JSON output validation
  - Help flag and argument parsing
  - Directory analysis
  - Config file loading and CLI overrides
  - Error handling for nonexistent paths

### Learning Outcomes
- Pytest framework and best practices
- Test coverage reporting and analysis
- GitHub Actions CI/CD workflows
- Pre-commit hooks configuration
- Code quality automation
- Multi-platform testing strategies
- Dogfooding (using your own tool)

---

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
