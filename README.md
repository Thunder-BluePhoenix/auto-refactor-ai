# Auto Refactor AI

[![PyPI version](https://img.shields.io/badge/pypi-v0.10.0-blue.svg)](https://pypi.org/project/auto-refactor-ai/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-289%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)]()

A comprehensive AI-powered static analyzer for Python code with refactoring suggestions, project analysis, and strategic planning.

## Current Version: V10 (0.10.0)

**Production-ready with strategic refactoring plans!** V10 adds `--plan` mode for generating AI-powered refactoring roadmaps with HTML report generation.

## Features

- **Multiple Analysis Rules**:
  - **Rule 1**: Long functions (configurable threshold, default: 30 lines)
  - **Rule 2**: Too many parameters (default: > 5 parameters)
  - **Rule 3**: Deep nesting (default: > 3 levels)

- **Severity Levels**: Issues are categorized as `INFO`, `WARN`, or `CRITICAL` based on how much they exceed thresholds
- **Configuration Files**: Support for `.auto-refactor-ai.toml`, `.auto-refactor-ai.yaml`, or `pyproject.toml`
- **JSON Output**: Machine-readable output for IDE integration and CI/CD pipelines
- **Directory Scanning**: Analyze entire projects recursively
- **Comprehensive Summary**: Get counts by severity level
- **Zero Dependencies**: Built only with Python standard library (Python 3.8+)

### V4 Quality Assurance Features

- **60+ Unit Tests**: Comprehensive test suite with pytest (88% coverage)
- **GitHub Actions CI/CD**: Automated testing on 15 combinations (3 OS × 5 Python versions)
- **Pre-commit Hooks**: Automatic code quality checks before commits
- **Code Formatting**: Black formatter configured
- **Linting**: Ruff for fast, comprehensive linting
- **Type Checking**: Mypy static type analysis
- **Dogfooding**: We use auto-refactor-ai to analyze itself!

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install auto-refactor-ai
```

That's it! You can now use `auto-refactor-ai` command globally.

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/auto-refactor-ai.git
cd auto-refactor-ai

# Install in development mode
pip install -e .
```

### Option 3: Install from Local Build

```bash
# Build the package
python -m build

# Install the wheel
pip install dist/auto_refactor_ai-0.3.0-py3-none-any.whl
```

## Usage

### Basic Usage

```bash
# Analyze a single file
auto-refactor-ai path/to/your_script.py

# Analyze an entire directory
auto-refactor-ai .

# The old way still works too
python -m auto_refactor_ai .
```

### Command-Line Options

```bash
# Customize thresholds
auto-refactor-ai . --max-len 20 --max-params 3 --max-nesting 2

# Use a specific config file
auto-refactor-ai . --config path/to/config.toml

# Output as JSON for tool integration
auto-refactor-ai . --format json

# Combine options
auto-refactor-ai . --config examples/config-strict.toml --format json

# Get help
auto-refactor-ai --help
```

**Available options:**
- `--max-len`: Maximum function length in lines (default: 30)
- `--max-params`: Maximum parameters per function (default: 5)
- `--max-nesting`: Maximum nesting depth (default: 3)
- `--config`: Path to config file (auto-discovered if not specified)
- `--format`: Output format - `text` or `json` (default: text)

### Configuration Files

Create a config file to set project-wide defaults. The analyzer automatically searches for config files in the current directory and parent directories.

**Option 1: `.auto-refactor-ai.toml`**

```toml
# Maximum allowed function length in lines
max_function_length = 25

# Maximum allowed number of parameters per function
max_parameters = 4

# Maximum allowed nesting depth
max_nesting_depth = 3

# List of enabled rules
enabled_rules = ["function-too-long", "too-many-parameters", "deep-nesting"]
```

**Option 2: `.auto-refactor-ai.yaml`**

```yaml
max_function_length: 30
max_parameters: 5
max_nesting_depth: 3

enabled_rules:
  - function-too-long
  - too-many-parameters
  - deep-nesting
```

**Option 3: `pyproject.toml`**

```toml
[tool.auto-refactor-ai]
max_function_length = 30
max_parameters = 5
max_nesting_depth = 3
```

See the [`examples/`](examples/) directory for sample configurations:
- `config-strict.toml` - High standards for new projects
- `config-relaxed.toml` - Lenient settings for legacy code

## Example Output

### Text Format (Human-Readable)

```
[CRITICAL] my_app/service.py:26-92  process_order()
  - Function 'process_order' is 67 lines long (max: 30). Consider splitting it into smaller functions with single responsibilities.

[WARN] my_app/utils.py:14-23  validate_data()
  - Function 'validate_data' has 5 levels of nesting (max: 3). High nesting makes code harder to understand. Consider extracting nested logic into helper functions.

[INFO] my_app/handlers.py:45-52  handle_request()
  - Function 'handle_request' has 7 parameters (recommended: ≤ 5). Consider grouping related parameters into a dataclass or config object.

============================================================
SUMMARY
============================================================
  CRITICAL: 1
  WARN:     4
  INFO:     8
  TOTAL:    13
============================================================
```

### JSON Format (Machine-Readable)

```json
{
  "config": {
    "max_function_length": 30,
    "max_parameters": 5,
    "max_nesting_depth": 3,
    "enabled_rules": ["function-too-long", "too-many-parameters", "deep-nesting"]
  },
  "summary": {
    "total": 13,
    "critical": 1,
    "warn": 4,
    "info": 8
  },
  "issues": [
    {
      "severity": "CRITICAL",
      "file": "my_app/service.py",
      "function_name": "process_order",
      "start_line": 26,
      "end_line": 92,
      "rule_name": "function-too-long",
      "message": "Function 'process_order' is 67 lines long...",
      "details": {
        "length": 67,
        "max_length": 30
      }
    }
  ]
}
```

## Development

### For Contributors

#### Install Development Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/auto-refactor-ai.git
cd auto-refactor-ai

# Install with dev dependencies
pip install -e ".[dev]"
```

#### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=auto_refactor_ai --cov-report=term-missing

# Run specific test file
pytest tests/test_analyzer.py -v
```

#### Code Quality Tools

```bash
# Format code with black
black auto_refactor_ai tests

# Lint with ruff
ruff check --fix auto_refactor_ai tests

# Type check with mypy
mypy auto_refactor_ai
```

#### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

#### Run Self-Analysis (Dogfooding)

```bash
# Analyze our own codebase
auto-refactor-ai auto_refactor_ai/

# With strict settings
auto-refactor-ai auto_refactor_ai/ --max-len 50
```

## What's New

### V4 (Current - 0.4.0)

V4 makes Auto Refactor AI production-ready with comprehensive testing and automation:

1. **Comprehensive Testing**:
   - 60+ unit tests with pytest
   - 88% code coverage (exceeds 80% requirement)
   - Tests for analyzer, config, and CLI modules
   - Edge case testing

2. **GitHub Actions CI/CD**:
   - Automated testing on push and PR
   - Multi-platform: Ubuntu, Windows, macOS
   - Multi-version: Python 3.8 - 3.12
   - Code quality checks (black, ruff, mypy)
   - Self-analysis job (dogfooding)

3. **Pre-commit Hooks**:
   - Automatic code formatting
   - Linting and type checking
   - Tests run before commits
   - Self-analysis with strict settings

4. **Code Quality**:
   - Black for formatting (100-char lines)
   - Ruff for linting
   - Mypy for type checking
   - All configured in pyproject.toml

### V3 (0.3.0)

V3 makes Auto Refactor AI a proper pip-installable package:

1. **Pip Installable**:
   - Install with `pip install auto-refactor-ai`
   - Global `auto-refactor-ai` command
   - No need for `python -m` anymore

2. **Professional Package**:
   - Proper `pyproject.toml` configuration
   - Console script entry point
   - MIT License
   - Ready for PyPI distribution

3. **Enhanced Documentation**:
   - Complete V1, V2, V3 implementation guides
   - Publishing guide for PyPI
   - Verification script for testing
   - Release checklist

### V2 (0.2.0)

V2 added configuration and output flexibility:

1. **Configuration File Support**:
   - Auto-discovery of config files
   - TOML and YAML formats
   - Integration with `pyproject.toml`
   - CLI arguments override configs

2. **JSON Output Mode**:
   - Machine-readable output
   - Perfect for CI/CD and IDE integration
   - Structured data with config, summary, and issues

### V1 (0.1.0)

V1 introduced multiple analysis rules:

1. **Three Analysis Rules**:
   - Rule 1: Function length
   - Rule 2: Too many parameters
   - Rule 3: Deep nesting

2. **Severity Levels**: INFO, WARN, CRITICAL
3. **Better Output**: Sorted by severity with summary

## Project Structure

```
auto-refactor-ai/
│
├─ auto_refactor_ai/
│   ├─ __init__.py      # Package initialization
│   ├─ __main__.py      # Module entry point
│   ├─ analyzer.py      # Core analysis logic with multiple rules
│   ├─ cli.py           # Command line interface
│   └─ config.py        # Configuration file handling (NEW in V2)
│
├─ test_files/          # Comprehensive test suite
│   ├─ README.md        # Test files documentation
│   ├─ test_perfect_code.py       # Examples of good code (no issues)
│   ├─ test_length_issues.py      # Tests for Rule 1 (function length)
│   ├─ test_parameter_issues.py   # Tests for Rule 2 (too many params)
│   ├─ test_nesting_issues.py     # Tests for Rule 3 (deep nesting)
│   ├─ test_combined_issues.py    # Multiple violations per function
│   ├─ test_edge_cases.py         # Edge cases and special scenarios
│   ├─ sample_test.py             # Legacy V0 test file
│   └─ test_sample.py             # V1 development test file
│
├─ examples/            # Sample configuration files (NEW in V2)
│   ├─ .auto-refactor-ai.yaml    # YAML config example
│   ├─ config-strict.toml        # Strict quality standards
│   └─ config-relaxed.toml       # Lenient for legacy code
│
├─ .auto-refactor-ai.toml  # Project config file
├─ pyproject.toml          # Package metadata
└─ README.md               # This file
```

## How It Works

1. **Configure** - Loads configuration from files or command-line arguments
2. **Parse** - Uses Python's `ast` module to build an Abstract Syntax Tree
3. **Analyze** - Applies multiple rules to each function:
   - Counts lines to detect long functions
   - Counts parameters to detect over-parameterization
   - Calculates nesting depth using AST visitor pattern
4. **Classify** - Assigns severity based on how much thresholds are exceeded
5. **Report** - Outputs issues in text or JSON format

## Analysis Rules

### Rule 1: Function Too Long

**What it checks**: Function length in lines of code

**Why it matters**: Long functions are harder to understand, test, and maintain. They often violate the Single Responsibility Principle.

**Severity**:
- INFO: 1-1.5x over limit
- WARN: 1.5-2x over limit
- CRITICAL: 2x+ over limit

**How to fix**: Break the function into smaller, focused functions with clear names and single responsibilities.

### Rule 2: Too Many Parameters

**What it checks**: Number of function parameters (including *args and **kwargs)

**Why it matters**: Functions with many parameters are harder to test, call correctly, and understand. They often indicate missing abstractions.

**Severity**:
- INFO: 1-1.5x over limit
- WARN: 1.5-2x over limit
- CRITICAL: 2x+ over limit

**How to fix**:
- Group related parameters into a dataclass or configuration object
- Split the function into multiple functions with fewer parameters
- Use builder pattern for complex object construction

### Rule 3: Deep Nesting

**What it checks**: Maximum depth of nested control structures (if/for/while/with)

**Why it matters**: Deep nesting increases cognitive load and makes code harder to follow. It often leads to bugs.

**Severity**:
- INFO: 1-1.5x over limit
- WARN: 1.5-2x over limit
- CRITICAL: 2x+ over limit

**How to fix**:
- Extract nested logic into helper functions
- Use early returns to reduce nesting (guard clauses)
- Invert conditionals where possible
- Consider using list comprehensions or generator expressions

## Use Cases

### CI/CD Integration

```bash
# In GitHub Actions, GitLab CI, etc.
auto-refactor-ai . --format json > analysis.json
# Parse JSON and fail build if critical issues found
```

### Pre-commit Hook

```bash
# Check only changed files
git diff --name-only | grep '\.py$' | xargs auto-refactor-ai
```

### IDE Integration

Use JSON output to create IDE extensions:
```bash
auto-refactor-ai current_file.py --format json
```

### Code Review

Generate reports for code review:
```bash
auto-refactor-ai src/ > code_review.txt
```

## Roadmap

- **V0**: ✅ Single rule (function length), basic CLI
- **V1**: ✅ Multiple rules, severity levels, improved output
- **V2**: ✅ Config files & JSON output
- **V3**: ✅ Pip installable package (CURRENT - v0.3.0)
- **V4**: 🚧 Tests & CI/CD (NEXT)
  - pytest test suite with >80% coverage
  - GitHub Actions workflow
  - Pre-commit hooks
  - Code quality checks (black, ruff)
- **V5**: Detailed explanations for each rule
- **V6**: AI-powered suggestions using LLMs
- **V7**: Auto-fix mode with automated refactoring
- **V8**: Project-level analysis & duplicate detection
- **V9**: Git integration & smart pre-commit hooks
- **V10**: Refactor planning mode
- **V11**: Editor/IDE integration (VS Code, etc.)
- **V12**: Community-ready release with marketing

## Learning Path

This project teaches Python development concepts:

**V0-V2 (Beginner):**
- ✅ Python AST module for code analysis
- ✅ CLI tools with argparse
- ✅ Software architecture (rule-based design)
- ✅ Enums and dataclasses
- ✅ AST visitor pattern
- ✅ Configuration management (TOML/YAML)
- ✅ Data serialization (JSON)

**V3-V4 (Intermediate):**
- Python packaging & distribution
- Testing with pytest
- CI/CD with GitHub Actions
- Code quality tooling

**V5-V12 (Advanced):**
- LLM integration
- Code transformation
- Git integration
- Editor tooling
- Open source community building

## Contributing

This is a learning project designed to help developers grow. Contributions are welcome!

**Ways to contribute:**
- Implement features from the roadmap
- Add new analysis rules
- Improve documentation
- Create tutorials or examples
- Report bugs or suggest features

## License

MIT License - Feel free to use this project for learning and experimentation.
