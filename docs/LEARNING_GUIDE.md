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

### 🧱 V4 - Testing & CI/CD

**Skills:**
- Unit testing
- Integration testing
- GitHub Actions
- Code coverage

#### Writing Tests with pytest

```python
# tests/test_analyzer.py
import pytest
from auto_refactor_ai.analyzer import analyze_file

def test_detect_long_function(tmp_path):
    # Create a temporary test file
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def long_function():
    # Line 1
    # Line 2
    # ... (many lines)
    # Line 50
    pass
""")

    # Run analyzer
    issues = analyze_file(str(test_file), max_function_length=20)

    # Assertions
    assert len(issues) == 1
    assert issues[0].function_name == "long_function"
    assert issues[0].length > 20

def test_no_issues_for_short_function(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def short():
    return 42
""")

    issues = analyze_file(str(test_file), max_function_length=20)
    assert len(issues) == 0
```

#### GitHub Actions CI

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=auto_refactor_ai tests/
```

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
