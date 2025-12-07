# V4 Implementation Guide - Testing & CI/CD

**Version:** 0.4.0
**Status:** ✅ Complete
**Date:** 2024

## Overview

V4 transforms auto-refactor-ai into a production-ready project by adding comprehensive testing, continuous integration, and code quality automation. This version ensures reliability and maintainability through automated testing and quality checks.

## Goals

- ✅ Comprehensive test suite with pytest
- ✅ 80%+ code coverage
- ✅ GitHub Actions CI/CD pipeline
- ✅ Pre-commit hooks for code quality
- ✅ Automated code formatting and linting
- ✅ Self-analysis (dogfooding)

## What's New in V4

### 1. Comprehensive Test Suite

Created a full pytest test suite with 60+ tests covering all functionality:

**Test Structure:**
```
tests/
├── __init__.py
├── test_analyzer.py    # 26 tests - analyzer functionality
├── test_config.py      # 22 tests - configuration management
└── test_cli.py         # 12 tests - CLI interface
```

**Test Coverage Breakdown:**

| Module | Coverage | Tests | Description |
|--------|----------|-------|-------------|
| `analyzer.py` | 98% | 26 | Core analysis engine, all rules |
| `cli.py` | 96% | 12 | CLI interface, output formats |
| `config.py` | 75% | 22 | Configuration loading and discovery |
| **Total** | **88%** | **60** | **Exceeds 80% requirement** |

### 2. Test Categories

#### A. Analyzer Tests ([test_analyzer.py](../../tests/test_analyzer.py))

**Test Classes:**
- `TestSeverity` - Severity enum values
- `TestIssue` - Issue dataclass and serialization
- `TestNestingVisitor` - AST visitor for nesting depth
- `TestCheckFunctionLength` - Function length detection
- `TestCheckTooManyParameters` - Parameter count detection
- `TestCheckDeepNesting` - Nesting depth detection
- `TestAnalyzeFile` - Full file analysis

**Example Test:**
```python
def test_function_over_limit_critical(self):
    """Test function way over limit (CRITICAL)."""
    # 70 lines = 2.33x over 30 = CRITICAL
    lines = ["def extremely_long():\n"]
    for i in range(68):
        lines.append(f"    x{i} = {i}\n")
    lines.append("    return x0\n")
    code = "".join(lines)

    tree = ast.parse(code)
    func = tree.body[0]
    issue = check_function_length(func, "test.py", max_length=30)
    assert issue is not None
    assert issue.severity == Severity.CRITICAL
    assert issue.details["actual_length"] == 70
```

#### B. Configuration Tests ([test_config.py](../../tests/test_config.py))

**Test Classes:**
- `TestConfig` - Config dataclass operations
- `TestParseSimpleToml` - TOML parser
- `TestLoadTomlConfig` - TOML file loading
- `TestFindConfigFile` - Config file discovery
- `TestLoadConfig` - Full config loading

**Example Test:**
```python
def test_load_pyproject_toml(self):
    """Test loading config from pyproject.toml."""
    toml_content = """
[tool.auto-refactor-ai]
max_function_length = 40
max_parameters = 7
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir) / "pyproject.toml"
        temp_path.write_text(toml_content)

        result = load_toml_config(temp_path)
        assert result is not None
        assert result["max_function_length"] == 40
```

#### C. CLI Tests ([test_cli.py](../../tests/test_cli.py))

**Test Classes:**
- `TestPrintIssues` - Text output formatting
- `TestPrintSummary` - Summary statistics
- `TestPrintJson` - JSON output format
- `TestMainCLI` - Full CLI integration

**Example Test:**
```python
def test_main_with_json_format(self, capsys):
    """Test running with JSON output format."""
    code = "def simple_function(x):\n    return x + 1"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        temp_path = f.name

    try:
        with patch("sys.argv", ["auto-refactor-ai", temp_path, "--format", "json"]):
            main()
            captured = capsys.readouterr()
            data = json.loads(captured.out)
            assert "config" in data
            assert "summary" in data
            assert "issues" in data
    finally:
        Path(temp_path).unlink()
```

### 3. GitHub Actions CI/CD

Created comprehensive CI/CD pipeline: [.github/workflows/test.yml](../../.github/workflows/test.yml)

**Three Jobs:**

#### Job 1: Multi-Platform Tests
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
```

Tests run on:
- **3 operating systems** (Linux, Windows, macOS)
- **5 Python versions** (3.8 - 3.12)
- **Total: 15 test combinations**

#### Job 2: Code Quality Checks
```yaml
- black --check          # Code formatting
- ruff check             # Linting
- mypy                   # Type checking
```

#### Job 3: Self-Analysis (Dogfooding)
```yaml
- auto-refactor-ai auto_refactor_ai/ --format json
- Check for critical issues
```

We use our own tool to analyze our codebase!

### 4. Pre-commit Hooks

Created [.pre-commit-config.yaml](../../.pre-commit-config.yaml) with automatic quality checks:

**Hooks Included:**

1. **General File Checks**
   - Trailing whitespace removal
   - End-of-file fixer
   - YAML/TOML validation
   - Large file detection
   - Merge conflict detection

2. **Code Formatting**
   - `black` - Auto-format Python code to 100-char lines

3. **Linting**
   - `ruff` - Fast Python linter with auto-fixes

4. **Type Checking**
   - `mypy` - Static type checking

5. **Self-Analysis** (Dogfooding!)
   - Run auto-refactor-ai on changed files
   - Use strict settings (`--max-len=50`)

6. **Test Execution**
   - Run pytest before every commit
   - Ensure 80%+ coverage

**Installation:**
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### 5. Code Quality Configuration

All tools configured in [pyproject.toml](../../pyproject.toml):

#### pytest Configuration
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--verbose",
    "--cov=auto_refactor_ai",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=80",
]
```

#### Coverage Configuration
```toml
[tool.coverage.run]
source = ["auto_refactor_ai"]
omit = ["tests/*", "test_files/*", "scripts/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
]
```

#### Black Configuration
```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
```

#### Ruff Configuration
```toml
[tool.ruff]
line-length = 100
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
]
```

#### Mypy Configuration
```toml
[tool.mypy]
python_version = "3.8"
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
```

## Running Tests

### Basic Test Run
```bash
pytest
```

### With Coverage Report
```bash
pytest --cov=auto_refactor_ai --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/test_analyzer.py
```

### Run Specific Test Class
```bash
pytest tests/test_analyzer.py::TestCheckFunctionLength
```

### Run Specific Test
```bash
pytest tests/test_analyzer.py::TestCheckFunctionLength::test_function_over_limit_critical
```

### Verbose Output
```bash
pytest -v
```

### See Print Statements
```bash
pytest -s
```

### Stop on First Failure
```bash
pytest -x
```

### Run in Parallel (with pytest-xdist)
```bash
pip install pytest-xdist
pytest -n auto
```

## Coverage Reports

### Terminal Report
```bash
pytest --cov=auto_refactor_ai --cov-report=term-missing
```

Output:
```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
auto_refactor_ai/__init__.py       2      0   100%
auto_refactor_ai/analyzer.py     110      2    98%   121, 158
auto_refactor_ai/cli.py           74      3    96%   60, 96-97
auto_refactor_ai/config.py       122     30    75%   55, 110, ...
------------------------------------------------------------
TOTAL                            309     36    88%
```

### HTML Report
```bash
pytest --cov=auto_refactor_ai --cov-report=html
open htmlcov/index.html  # View in browser
```

### XML Report (for CI/CD)
```bash
pytest --cov=auto_refactor_ai --cov-report=xml
```

## Code Quality Tools

### Run Black (Formatting)
```bash
# Check formatting
black --check auto_refactor_ai tests

# Auto-format
black auto_refactor_ai tests
```

### Run Ruff (Linting)
```bash
# Check for issues
ruff check auto_refactor_ai tests

# Auto-fix issues
ruff check --fix auto_refactor_ai tests
```

### Run Mypy (Type Checking)
```bash
mypy auto_refactor_ai
```

### Run All Quality Checks
```bash
black --check auto_refactor_ai tests && \
ruff check auto_refactor_ai tests && \
mypy auto_refactor_ai && \
pytest --cov=auto_refactor_ai --cov-fail-under=80
```

## Dogfooding - Self-Analysis

We use auto-refactor-ai to analyze its own codebase:

```bash
# Analyze our own code
auto-refactor-ai auto_refactor_ai/

# With strict settings
auto-refactor-ai auto_refactor_ai/ --max-len 50 --max-params 3

# JSON output for CI/CD
auto-refactor-ai auto_refactor_ai/ --format json > self-analysis.json
```

This ensures we follow our own best practices!

## CI/CD Pipeline

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

### What Runs
1. **Tests** on 15 combinations (3 OS × 5 Python versions)
2. **Code quality checks** (black, ruff, mypy)
3. **Self-analysis** (dogfooding)
4. **Coverage upload** to Codecov

### Viewing Results
- Check GitHub Actions tab
- See test results for each commit
- View coverage trends on Codecov

## Development Workflow

### With Pre-commit Hooks

1. **Make changes** to code
2. **Stage changes**: `git add .`
3. **Commit**: `git commit -m "message"`
   - Pre-commit hooks run automatically
   - Black formats code
   - Ruff checks for issues
   - Tests run
   - If anything fails, commit is blocked
4. **Fix issues** if hooks fail
5. **Try commit again**

### Without Pre-commit Hooks

```bash
# 1. Make changes
# 2. Run tests
pytest

# 3. Check formatting
black auto_refactor_ai tests

# 4. Check linting
ruff check --fix auto_refactor_ai tests

# 5. Check coverage
pytest --cov=auto_refactor_ai --cov-fail-under=80

# 6. Commit
git add .
git commit -m "Your message"
```

## Key Files Added/Modified

### New Files
```
.github/workflows/test.yml       # GitHub Actions CI/CD
.pre-commit-config.yaml          # Pre-commit hooks
tests/__init__.py                # Test package
tests/test_analyzer.py           # Analyzer tests (26 tests)
tests/test_config.py             # Config tests (22 tests)
tests/test_cli.py                # CLI tests (12 tests)
```

### Modified Files
```
pyproject.toml                   # Updated to v0.4.0, added test config
```

## Test Statistics

- **Total Tests:** 60
- **Test Files:** 3
- **Test Classes:** 19
- **Code Coverage:** 88%
- **Coverage Requirement:** 80%
- **Status:** ✅ All tests passing

## Dependencies Added

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",           # Test framework
    "pytest-cov>=4.0",       # Coverage plugin
    "pytest-mock>=3.10",     # Mocking utilities
    "black>=23.0",           # Code formatter
    "ruff>=0.1.0",           # Fast linter
    "mypy>=1.0",             # Type checker
    "pre-commit>=3.0",       # Pre-commit hooks
]
```

Install all dev dependencies:
```bash
pip install -e ".[dev]"
```

## Testing Best Practices

### 1. Arrange-Act-Assert Pattern
```python
def test_example():
    # Arrange - Set up test data
    code = "def foo(): pass"

    # Act - Execute the code
    result = analyze_file(code)

    # Assert - Verify results
    assert len(result) == 0
```

### 2. Use Fixtures
```python
@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        yield f.name
    Path(f.name).unlink()

def test_with_fixture(temp_file):
    # Use temp_file
    pass
```

### 3. Test Edge Cases
- Empty input
- Invalid input
- Boundary conditions
- Error conditions

### 4. Descriptive Test Names
```python
def test_function_over_limit_critical():  # Good
def test_func():                           # Bad
```

### 5. Use Mocking
```python
from unittest.mock import patch

def test_with_mock():
    with patch("sys.argv", ["prog", "--help"]):
        # Test code
        pass
```

## Common Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific file
pytest tests/test_analyzer.py

# Run tests matching pattern
pytest -k "test_function_length"

# Show print statements
pytest -s

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Show local variables on failure
pytest -l
```

## Continuous Integration Benefits

1. **Catch bugs early** - Tests run on every commit
2. **Multi-platform support** - Verify on Linux, Windows, macOS
3. **Python version compatibility** - Test 3.8 through 3.12
4. **Code quality enforcement** - Auto-check formatting and linting
5. **Coverage tracking** - Maintain 80%+ coverage
6. **Automated dogfooding** - Self-analysis on every push

## Next Steps (V5)

After completing V4, the next version will add:

- **Detailed Explanations**: Each issue gets a detailed explanation
- **Example Code**: Show good vs bad code examples
- **Fix Suggestions**: Automated refactoring suggestions
- **Rule Documentation**: In-depth rule explanations
- **Custom Rules**: User-defined rules API

See [V5_GUIDE.md](V5_GUIDE.md) when available.

## Troubleshooting

### Tests Fail Locally
```bash
# Check which tests fail
pytest -v

# Run specific failing test
pytest tests/test_analyzer.py::TestCheckFunctionLength -v

# See full error output
pytest -vv
```

### Coverage Too Low
```bash
# See which lines are not covered
pytest --cov=auto_refactor_ai --cov-report=term-missing

# View HTML report for details
pytest --cov=auto_refactor_ai --cov-report=html
open htmlcov/index.html
```

### Pre-commit Hooks Fail
```bash
# Run hooks manually to see details
pre-commit run --all-files

# Update hooks
pre-commit autoupdate

# Skip hooks (not recommended)
git commit --no-verify
```

### GitHub Actions Fail
- Check Actions tab on GitHub
- View logs for failing jobs
- Test locally with same Python version
- Ensure all tests pass locally first

## Summary

V4 successfully transforms auto-refactor-ai into a production-ready project with:

✅ **60 comprehensive tests** covering all functionality
✅ **88% code coverage** (exceeds 80% requirement)
✅ **GitHub Actions CI/CD** testing on 15 combinations
✅ **Pre-commit hooks** for automatic quality checks
✅ **Code quality tools** (black, ruff, mypy)
✅ **Dogfooding** - we use our own tool!

The project now has:
- Reliable, tested code
- Automated quality enforcement
- Multi-platform compatibility
- Continuous integration
- Professional development workflow

**V4 Status: Complete ✅**
