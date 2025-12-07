# Learning Guide

Master Python development through building Auto Refactor AI.

---

## 🎯 What You'll Learn

This project is designed to teach you:

1. **Python Fundamentals** → AST, modules, packages
2. **Software Engineering** → Architecture, testing, CI/CD
3. **AI Integration** → LLMs, prompt engineering
4. **Dev Tools** → CLI tools, IDE extensions
5. **Open Source** → Packaging, distribution, community

---

## 📚 Learning by Version

Each version focuses on specific skills.

---

### 🧱 V0 - Python AST Basics

**Skills:**
- Abstract Syntax Trees (AST)
- File I/O and encoding
- Basic data structures
- Error handling

#### Understanding AST

The AST (Abstract Syntax Tree) is how Python internally represents your code.

**Example:**

```python
# This Python code...
def add(a, b):
    return a + b
```

**...becomes this AST:**
```
Module
  └── FunctionDef(name='add')
      ├── arguments
      │   ├── arg(arg='a')
      │   └── arg(arg='b')
      └── Return
          └── BinOp
              ├── left: Name(id='a')
              ├── op: Add()
              └── right: Name(id='b')
```

**Try It:**
```python
import ast

code = """
def add(a, b):
    return a + b
"""

tree = ast.parse(code)
print(ast.dump(tree, indent=2))
```

#### Walking the AST

`ast.walk()` visits every node:

```python
import ast

code = """
def greet(name):
    if name:
        return f"Hello, {name}!"
    return "Hello!"
"""

tree = ast.parse(code)

# Find all function definitions
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(f"Found function: {node.name}")
        print(f"  Lines: {node.lineno} to {node.end_lineno}")
        print(f"  Parameters: {len(node.args.args)}")
```

#### Exercise: Count If Statements

**Challenge:** Write a function that counts how many `if` statements are in a Python file.

<details>
<summary>Solution</summary>

```python
import ast

def count_if_statements(filename: str) -> int:
    with open(filename, 'r') as f:
        tree = ast.parse(f.read())

    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            count += 1

    return count
```
</details>

---

### 🧱 V1 - Software Architecture

**Skills:**
- Object-oriented design
- Plugin architecture
- Separation of concerns
- Code organization

#### The Rule Pattern

Instead of hardcoding rules in one function, we create a **Rule** interface:

```python
from abc import ABC, abstractmethod
from typing import List
import ast

class Issue:
    """Represents a code issue."""
    def __init__(self, message: str, line: int):
        self.message = message
        self.line = line

class Rule(ABC):
    """Base class for all rules."""

    @abstractmethod
    def check(self, node: ast.AST) -> List[Issue]:
        """Check a node and return issues found."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this rule."""
        pass
```

#### Implementing a Rule

```python
class TooManyParametersRule(Rule):
    def __init__(self, max_params: int = 5):
        self.max_params = max_params

    @property
    def name(self) -> str:
        return "too_many_parameters"

    def check(self, node: ast.AST) -> List[Issue]:
        if not isinstance(node, ast.FunctionDef):
            return []

        param_count = len(node.args.args)
        if param_count > self.max_params:
            return [Issue(
                f"Function '{node.name}' has {param_count} parameters (max: {self.max_params})",
                node.lineno
            )]

        return []
```

#### Using the Rule System

```python
rules = [
    FunctionLengthRule(max_length=30),
    TooManyParametersRule(max_params=5),
    DeepNestingRule(max_depth=3)
]

tree = ast.parse(source_code)
all_issues = []

for node in ast.walk(tree):
    for rule in rules:
        all_issues.extend(rule.check(node))
```

**Benefits:**
- ✅ Easy to add new rules
- ✅ Rules can be independently tested
- ✅ Rules can be enabled/disabled
- ✅ Clean, maintainable code

#### Exercise: Create a Rule

**Challenge:** Create a `TooManyReturnsRule` that warns if a function has more than N return statements.

<details>
<summary>Hint</summary>

You'll need to:
1. Check if node is a `FunctionDef`
2. Walk the function's body
3. Count `ast.Return` nodes
4. Compare to threshold
</details>

<details>
<summary>Solution</summary>

```python
class TooManyReturnsRule(Rule):
    def __init__(self, max_returns: int = 3):
        self.max_returns = max_returns

    @property
    def name(self) -> str:
        return "too_many_returns"

    def check(self, node: ast.AST) -> List[Issue]:
        if not isinstance(node, ast.FunctionDef):
            return []

        return_count = sum(
            1 for n in ast.walk(node)
            if isinstance(n, ast.Return)
        )

        if return_count > self.max_returns:
            return [Issue(
                f"Function '{node.name}' has {return_count} return statements (max: {self.max_returns})",
                node.lineno
            )]

        return []
```
</details>

---

### 🧱 V2 - Configuration & Data Formats

**Skills:**
- TOML/YAML parsing
- JSON serialization
- Data validation
- Configuration management

#### Reading TOML Config

```python
import tomli  # pip install tomli

def load_config(path: str) -> dict:
    with open(path, "rb") as f:
        return tomli.load(f)

# .auto_refactor_ai.toml
config = load_config(".auto_refactor_ai.toml")
max_length = config["rules"]["length"]["max_length"]
```

#### JSON Output

```python
import json
from dataclasses import asdict

@dataclass
class Issue:
    file: str
    line: int
    message: str
    severity: str

# Convert to JSON
issues = [Issue("test.py", 10, "Too long", "WARN")]
json_output = json.dumps([asdict(i) for i in issues], indent=2)
print(json_output)
```

**Output:**
```json
[
  {
    "file": "test.py",
    "line": 10,
    "message": "Too long",
    "severity": "WARN"
  }
]
```

#### Exercise: Config Validation

**Challenge:** Write a function that validates a config file has all required fields.

---

### 🧱 V3 - Python Packaging

**Skills:**
- Package structure
- Entry points
- Distribution
- Publishing to PyPI

#### `pyproject.toml` Explained

```toml
[build-system]
requires = ["setuptools>=61.0"]  # Build dependencies
build-backend = "setuptools.build_meta"

[project]
name = "auto-refactor-ai"        # Package name on PyPI
version = "0.1.0"                # Semantic versioning
description = "..."
requires-python = ">=3.8"        # Minimum Python version

[project.scripts]
auto-refactor-ai = "auto_refactor_ai:main"  # CLI command
#    ↑ command         ↑ package  ↑ function
```

#### Building & Installing

```bash
# Install build tools
pip install build

# Build the package
python -m build

# This creates:
# dist/auto_refactor_ai-0.1.0.tar.gz
# dist/auto_refactor_ai-0.1.0-py3-none-any.whl

# Install locally
pip install dist/auto_refactor_ai-0.1.0-py3-none-any.whl

# Now you can run:
auto-refactor-ai --help
```

#### Publishing to TestPyPI

```bash
# Install twine
pip install twine

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ auto-refactor-ai
```

---

### 🧱 V4 - Testing & CI/CD (✅ IMPLEMENTED)

**Status:** Complete in v0.4.0
**Achievement:** 60 tests, 88% coverage, multi-platform CI/CD

**Skills:**
- Unit testing with pytest
- Test coverage analysis
- GitHub Actions workflows
- Pre-commit hooks
- Code quality automation
- Test-Driven Development (TDD)
- Mocking and fixtures
- Multi-platform testing

#### Writing Comprehensive Tests

**Test Structure:**
```
tests/
├── test_analyzer.py   # 26 tests - Core analysis
├── test_config.py     # 22 tests - Configuration
└── test_cli.py        # 12 tests - CLI interface
```

**Example 1: Testing with Arrange-Act-Assert Pattern**

```python
# tests/test_analyzer.py
import pytest
import ast
from auto_refactor_ai.analyzer import check_function_length, Severity

def test_function_over_limit_critical():
    """Test function way over limit (CRITICAL)."""
    # Arrange - Create test data
    lines = ["def extremely_long():\n"]
    for i in range(68):
        lines.append(f"    x{i} = {i}\n")
    lines.append("    return x0\n")
    code = "".join(lines)

    # Act - Execute code under test
    tree = ast.parse(code)
    func = tree.body[0]
    issue = check_function_length(func, "test.py", max_length=30)

    # Assert - Verify results
    assert issue is not None
    assert issue.severity == Severity.CRITICAL
    assert issue.details["actual_length"] == 70
    assert "extremely_long" in issue.message
```

**Example 2: Using Fixtures for Reusable Setup**

```python
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_config_file():
    """Create temporary config file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False
    ) as f:
        f.write("max_function_length = 40\n")
        f.write("max_parameters = 7\n")
        f.flush()
        yield Path(f.name)
    Path(f.name).unlink()

def test_load_config_from_file(temp_config_file):
    """Test loading configuration from file."""
    config = load_toml_config(temp_config_file)
    assert config["max_function_length"] == 40
    assert config["max_parameters"] == 7
```

**Example 3: Mocking for CLI Tests**

```python
from unittest.mock import patch

def test_main_with_help(self):
    """Test running with --help flag."""
    with patch("sys.argv", ["auto-refactor-ai", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
```

#### Test Coverage Analysis

**Run tests with coverage:**
```bash
pytest --cov=auto_refactor_ai --cov-report=term-missing
```

**Output:**
```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
auto_refactor_ai/analyzer.py     110      2    98%   121, 158
auto_refactor_ai/cli.py           74      3    96%   60, 96-97
auto_refactor_ai/config.py       122     30    75%   55, 110, ...
------------------------------------------------------------
TOTAL                            309     36    88%
```

**Coverage Best Practices:**
- Aim for 80%+ coverage
- Focus on critical paths
- Test edge cases
- Don't chase 100% (diminishing returns)
- Use `# pragma: no cover` for defensive code

#### GitHub Actions CI/CD

**Multi-Platform Testing:**

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    name: Test on ${{ matrix.os }} with Python ${{ matrix.python-version }}
    runs-on: ${{ matrix.os }}

    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"

    - name: Run tests
      run: |
        pytest --cov=auto_refactor_ai --cov-report=xml

  lint:
    name: Code Quality Checks
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: pip install -e ".[dev]"

    - name: Run black
      run: black --check auto_refactor_ai tests

    - name: Run ruff
      run: ruff check auto_refactor_ai tests

    - name: Run mypy
      run: mypy auto_refactor_ai

  dogfood:
    name: Self-Analysis
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
    - run: pip install -e .
    - run: auto-refactor-ai auto_refactor_ai/ --format json > self.json
    - run: python -c "import json; exit(json.load(open('self.json'))['summary']['critical'])"
```

**Key Concepts:**
- **Matrix Testing:** Test on multiple OS and Python versions
- **Fail-Fast:** Set to false to see all failures
- **Codecov Integration:** Upload coverage for tracking
- **Dogfooding:** Use your own tool to test itself

#### Pre-commit Hooks

**Configuration:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml

  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: ['--fix']

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        args: ['--cov=auto_refactor_ai', '--cov-fail-under=80', '-q']
```

**Install pre-commit:**
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

#### Key Learnings from V4

**1. Test-Driven Development (TDD)**
- Write tests first
- See them fail (Red)
- Implement minimal code to pass (Green)
- Refactor while keeping tests green

**2. Testing Best Practices**
- **Arrange-Act-Assert** pattern for clarity
- **Fixtures** for reusable test setup
- **Mocking** for external dependencies
- **Parametrized tests** for multiple scenarios
- **Descriptive test names** that explain what's being tested

**3. Coverage is a Guide, Not a Goal**
- 80%+ is good enough
- Focus on critical code paths
- Test edge cases and error conditions
- Don't test framework code

**4. CI/CD Benefits**
- Catch bugs before merging
- Multi-platform compatibility verification
- Automated code quality enforcement
- Confidence in refactoring

**5. Pre-commit Hooks Save Time**
- Catch issues before commit
- Auto-format code
- Run quick tests locally
- Prevent broken commits

#### Exercises

**Exercise 1: Add a New Test**
Write a test for detecting functions with too many parameters (>5).

**Exercise 2: Achieve 90% Coverage**
Identify uncovered lines and write tests for them.

**Exercise 3: Create a Custom Pre-commit Hook**
Add a hook that prevents committing debug print statements.

**Exercise 4: Add Codecov Badge**
Set up Codecov integration and add badge to README.

---

### 🤖 V6 - LLM Integration

**Skills:**
- API integration
- Async programming
- Error handling
- Prompt engineering

#### Basic OpenAI Integration

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

def get_refactor_suggestion(code: str, issue: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a Python refactoring expert. Suggest improvements to code."
            },
            {
                "role": "user",
                "content": f"Code:\n{code}\n\nIssue: {issue}\n\nSuggest refactoring:"
            }
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content
```

#### Prompt Engineering

**Bad Prompt:**
```
Fix this code.
```

**Good Prompt:**
```
Refactor this Python function to improve readability and maintainability.

Current code:
{code}

Issues detected:
- Function is 80 lines long
- Has 7 parameters
- Nesting depth of 5

Please:
1. Split into smaller, focused functions
2. Use dataclasses for parameter grouping
3. Reduce nesting with early returns
4. Preserve original behavior
5. Return only the refactored code with brief comments
```

#### Exercise: Anthropic Integration

**Challenge:** Implement the same functionality using Anthropic's Claude API.

<details>
<summary>Solution</summary>

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

def get_refactor_suggestion(code: str, issue: str) -> str:
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"Code:\n{code}\n\nIssue: {issue}\n\nSuggest refactoring:"
            }
        ]
    )

    return message.content[0].text
```
</details>

---

## 🎓 Concepts Explained

### Cyclomatic Complexity

Measures code complexity by counting decision points.

**Formula:**
```
Complexity = Number of decision points + 1
```

**Decision points:**
- `if`, `elif`
- `for`, `while`
- `and`, `or`
- `try`, `except`

**Example:**
```python
def simple():
    return 42
# Complexity: 1 (no decisions)

def with_if(x):
    if x > 0:
        return x
    return 0
# Complexity: 2 (one if)

def complex(x, y):
    if x > 0 and y > 0:
        if x > y:
            return x
        return y
    elif x < 0:
        return 0
    return y
# Complexity: 5
```

**Computing with AST:**
```python
def calculate_complexity(node: ast.FunctionDef) -> int:
    complexity = 1

    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(child, (ast.And, ast.Or)):
            complexity += 1

    return complexity
```

### Code Smells

Common patterns that indicate potential problems:

1. **Long Function** - Hard to understand, test, and maintain
2. **Too Many Parameters** - Hard to remember and use
3. **Deep Nesting** - Complex control flow
4. **Duplicate Code** - Maintenance nightmare
5. **God Object** - Does too much
6. **Magic Numbers** - Unexplained constants

---

## 🛠️ Practical Exercises

### Exercise 1: Nesting Depth Detector

**Goal:** Detect functions with nesting depth > 3

**Hints:**
- Track current depth as you walk the AST
- Increment on `If`, `For`, `While`, `With`, `Try`
- Decrement when leaving those blocks

### Exercise 2: Duplicate Code Finder

**Goal:** Find functions with identical ASTs

**Hints:**
- Normalize AST (remove variable names)
- Hash the normalized AST
- Compare hashes

### Exercise 3: Import Organizer

**Goal:** Analyze and report on import statements

**Hints:**
- Look for `ast.Import` and `ast.ImportFrom`
- Check for unused imports
- Suggest grouping (stdlib, third-party, local)

---

## 📖 Resources

### Python AST
- [Official AST docs](https://docs.python.org/3/library/ast.html)
- [Green Tree Snakes](https://greentreesnakes.readthedocs.io/) - AST tutorial
- [AST Explorer](https://python-ast-explorer.com/) - Visual AST viewer

### Software Architecture
- [Clean Code](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882) by Robert Martin
- [Refactoring](https://refactoring.com/) by Martin Fowler
- [Design Patterns](https://refactoring.guru/design-patterns)

### Testing
- [pytest documentation](https://docs.pytest.org/)
- [Test-Driven Development](https://www.obeythetestinggoat.com/)

### Python Packaging
- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI](https://pypi.org/)

### LLM Integration
- [OpenAI API docs](https://platform.openai.com/docs)
- [Anthropic API docs](https://docs.anthropic.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

## 🎯 Next Steps

1. **Master V0** - Understand AST deeply
2. **Implement V1** - Build the rule system
3. **Add Tests (V4)** - Practice TDD
4. **Integrate LLM (V6)** - Learn AI APIs
5. **Build Editor Extension (V11)** - Create dev tools

---

## 💡 Tips for Learning

1. **Read the code** - Don't just copy-paste
2. **Experiment** - Break things and fix them
3. **Add features** - Think of your own rules
4. **Ask questions** - Use GitHub Discussions
5. **Teach others** - Write blog posts, make videos

---

## 🤝 Community

- **GitHub Discussions** - Ask questions, share ideas
- **Discord** - Real-time chat (coming soon)
- **Blog** - Deep-dive articles (coming soon)

Happy learning! 🚀
