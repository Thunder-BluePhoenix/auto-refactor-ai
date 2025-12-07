# Architecture Guide

Understanding the internals of Auto Refactor AI.

---

## 📁 Project Structure

```
auto-refactor-ai/
│
├── auto_refactor_ai/          # Main package
│   ├── __init__.py            # Package initialization, exports main()
│   ├── __main__.py            # Entry point for python -m auto_refactor_ai
│   ├── analyzer.py            # Core analysis logic
│   └── cli.py                 # Command-line interface
│
├── docs/                      # Documentation
│   ├── ROADMAP.md            # Full version roadmap
│   ├── ARCHITECTURE.md       # This file
│   ├── LEARNING_GUIDE.md     # Educational content
│   ├── API_REFERENCE.md      # Code documentation
│   ├── versions/             # Version-specific guides
│   └── learning/             # Learning materials
│
├── tests/                     # Test suite (V4+)
│   ├── test_analyzer.py
│   ├── test_rules.py
│   └── test_cli.py
│
├── pyproject.toml            # Package metadata & dependencies
├── README.md                 # Main documentation
├── QUICKSTART.md            # Quick start guide
├── sample_test.py           # Sample file for testing
└── .gitignore               # Git ignore patterns
```

---

## 🏗️ Core Components (V0)

### 1. `analyzer.py` - The Brain

**Purpose:** Analyze Python source code and detect issues.

**Key Classes:**

#### `FunctionIssue` (dataclass)
Represents a single code issue found during analysis.

```python
@dataclass
class FunctionIssue:
    file: str              # Path to file
    function_name: str     # Name of the function
    start_line: int        # Starting line number
    end_line: int          # Ending line number
    length: int            # Number of lines
    message: str           # Human-readable description
```

**Key Functions:**

#### `analyze_file(path: str, max_function_length: int = 30) -> List[FunctionIssue]`

**Flow:**
1. Read file contents
2. Parse into AST (Abstract Syntax Tree)
3. Walk the AST to find all function definitions
4. Check each function against rules
5. Return list of issues

**Error Handling:**
- Catches `SyntaxError` for invalid Python files
- Returns empty list on error

**Example:**
```python
issues = analyze_file("my_script.py", max_function_length=25)
for issue in issues:
    print(f"{issue.function_name} is {issue.length} lines long")
```

---

### 2. `cli.py` - The Interface

**Purpose:** Provide command-line interface for users.

**Key Functions:**

#### `main()`
Entry point for CLI. Sets up argument parser and routes to appropriate handler.

**Arguments:**
- `path` (positional): File or directory to analyze
- `--max-len` (optional): Maximum function length threshold (default: 30)

#### `analyze_single_file(path: Path, max_len: int)`
Analyzes a single Python file and prints results.

#### `analyze_directory(root: Path, max_len: int)`
Recursively finds all `.py` files in directory and analyzes each.

**Features:**
- Handles both files and directories
- Graceful error messages
- Clean, formatted output

#### `print_issues(issues: List[FunctionIssue])`
Formats and displays issues in human-readable format.

**Output Format:**
```
[LONG FUNCTION] path/to/file.py:10-50
  - Function : function_name
  - Length   : 41 lines
  - Suggestion: Consider splitting...
```

---

### 3. `__init__.py` - Package Entry

Exports the `main()` function to make the package executable.

```python
from .cli import main
__all__ = ["main"]
```

---

### 4. `__main__.py` - Module Execution

Enables running the package as a module:

```bash
python -m auto_refactor_ai
```

Implementation:
```python
from .cli import main

if __name__ == "__main__":
    main()
```

---

## 🧠 How It Works: Deep Dive

### The AST (Abstract Syntax Tree)

Python's `ast` module parses source code into a tree structure.

**Example:**

**Python Code:**
```python
def greet(name):
    return f"Hello, {name}!"
```

**AST Structure:**
```
Module
└── FunctionDef(name='greet')
    ├── arguments
    │   └── arg(arg='name')
    └── Return
        └── JoinedStr (f-string)
```

### Walking the AST

`ast.walk(tree)` yields every node in the tree:

```python
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        # Found a function!
        print(node.name, node.lineno)
```

**Node Types We Care About:**
- `ast.FunctionDef` - Regular functions
- `ast.AsyncFunctionDef` - Async functions (V1+)
- `ast.ClassDef` - Classes (V1+)
- `ast.If`, `ast.For`, `ast.While` - Control flow (V1+ for nesting)

### Line Number Tracking

Python 3.8+ provides:
- `node.lineno` - Starting line
- `node.end_lineno` - Ending line

**Fallback for older versions:**
```python
end = getattr(node, "end_lineno", start)
```

---

## 🎯 Design Principles

### 1. Single Responsibility
Each module has one clear purpose:
- `analyzer.py` - Analysis logic only
- `cli.py` - User interface only

### 2. Data-Driven
Issues are represented as data (`FunctionIssue`), not printed directly.
This allows for:
- Different output formats (text, JSON, HTML)
- Filtering and sorting
- Machine-readable results

### 3. Fail-Safe
- Invalid Python files don't crash the program
- Missing files show clear error messages
- Each file analyzed independently

### 4. Extensible
Easy to add new rules (see V1 architecture below).

---

## 🔮 Future Architecture (V1+)

### Rule-Based System (V1)

**New Structure:**
```
auto_refactor_ai/
├── rules/
│   ├── __init__.py
│   ├── base.py              # Base Rule class
│   ├── length_rule.py       # Function length rule
│   ├── parameters_rule.py   # Too many parameters
│   ├── nesting_rule.py      # Deep nesting
│   └── complexity_rule.py   # Cyclomatic complexity
```

**Base Rule Interface:**
```python
class Rule(ABC):
    @abstractmethod
    def check(self, node: ast.AST) -> List[Issue]:
        """Check a node and return issues."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Rule identifier."""
        pass

    @property
    def severity(self) -> str:
        """INFO, WARN, or CRITICAL."""
        return "WARN"
```

**Usage:**
```python
rules = [
    FunctionLengthRule(max_length=30),
    TooManyParametersRule(max_params=5),
    DeepNestingRule(max_depth=3)
]

for rule in rules:
    issues.extend(rule.check(node))
```

**Benefits:**
- Easy to add new rules
- Rules can be enabled/disabled
- Rules can be configured independently
- Clean separation of concerns

---

### Config System (V2)

**Config File (`.auto_refactor_ai.toml`):**
```toml
[rules.length]
enabled = true
max_length = 30
severity = "WARN"

[rules.parameters]
enabled = true
max_params = 5
severity = "WARN"

[rules.nesting]
enabled = true
max_depth = 3
severity = "CRITICAL"

[output]
format = "text"  # or "json"
show_severity = true
color = true
```

**Config Loader:**
```python
class Config:
    def __init__(self, config_path: Optional[Path] = None):
        self.rules = {}
        self.output = {}
        self._load(config_path)

    def _load(self, path: Optional[Path]):
        if path and path.exists():
            with open(path, "rb") as f:
                data = tomli.load(f)
                self.rules = data.get("rules", {})
                self.output = data.get("output", {})
        else:
            self._load_defaults()
```

---

### JSON Output (V2)

**Structure:**
```json
{
  "version": "0.2.0",
  "analyzed_files": 15,
  "total_issues": 23,
  "issues": [
    {
      "file": "my_app/service.py",
      "function": "process_order",
      "start_line": 12,
      "end_line": 50,
      "severity": "WARN",
      "rule": "length",
      "message": "Function is 39 lines long",
      "suggestion": "Consider splitting..."
    }
  ],
  "summary": {
    "critical": 2,
    "warn": 15,
    "info": 6
  }
}
```

---

### LLM Integration (V6)

**Provider Abstraction:**
```python
class LLMProvider(ABC):
    @abstractmethod
    async def suggest_refactor(self, code: str, issue: Issue) -> str:
        """Get refactoring suggestion from LLM."""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    async def suggest_refactor(self, code: str, issue: Issue) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": REFACTOR_PROMPT},
                {"role": "user", "content": f"Code:\n{code}\n\nIssue: {issue.message}"}
            ]
        )
        return response.choices[0].message.content
```

---

## 🧪 Testing Architecture (V4)

**Test Structure:**
```
tests/
├── fixtures/              # Sample Python files for testing
│   ├── long_function.py
│   ├── many_params.py
│   └── deep_nesting.py
│
├── test_analyzer.py      # Core logic tests
├── test_rules.py         # Individual rule tests
├── test_cli.py           # CLI integration tests
└── test_config.py        # Config loading tests
```

**Example Test:**
```python
def test_detect_long_function():
    issues = analyze_file("tests/fixtures/long_function.py", max_function_length=20)
    assert len(issues) == 1
    assert issues[0].function_name == "very_long_function"
    assert issues[0].length > 20
```

---

## 📊 Data Flow

### V0 Data Flow

```
User Input (CLI)
    ↓
Parse Arguments
    ↓
Find Python Files
    ↓
For Each File:
    ├─→ Read File
    ├─→ Parse to AST
    ├─→ Walk AST
    ├─→ Check Rules
    └─→ Collect Issues
    ↓
Format Issues
    ↓
Print to Console
```

### V1+ Data Flow (with Rules)

```
User Input (CLI)
    ↓
Load Config
    ↓
Initialize Rules
    ↓
Find Python Files
    ↓
For Each File:
    ├─→ Read File
    ├─→ Parse to AST
    ├─→ For Each Rule:
    │      ├─→ Check Rule
    │      └─→ Collect Issues
    └─→ Aggregate Issues
    ↓
Sort/Filter Issues
    ↓
Format Output (Text/JSON)
    ↓
Display Results
```

---

## 🔧 Key Technologies

| Technology | Purpose | Introduced |
|------------|---------|------------|
| `ast` | Parse Python code | V0 |
| `argparse` | CLI argument parsing | V0 |
| `pathlib` | Path operations | V0 |
| `dataclasses` | Data structures | V0 |
| `tomli` | TOML config parsing | V2 |
| `pytest` | Testing | V4 |
| `openai` / `anthropic` | LLM integration | V6 |
| `difflib` | Generate patches | V7 |
| `gitpython` | Git integration | V9 |

---

## 🎓 Learning Path

1. **Start Here:** Understand `analyzer.py` and how AST works
2. **Then:** Understand `cli.py` and argument parsing
3. **Next:** Study rule architecture (V1)
4. **Advanced:** LLM integration and code transformation

---

## 🤝 Extending the Project

### Adding a New Rule (V1+)

1. Create new file in `auto_refactor_ai/rules/`
2. Inherit from `Rule` base class
3. Implement `check()` method
4. Register in `rules/__init__.py`
5. Add tests
6. Update documentation

**Template:**
```python
from .base import Rule, Issue

class MyCustomRule(Rule):
    def __init__(self, threshold: int):
        self.threshold = threshold

    @property
    def name(self) -> str:
        return "my_custom_rule"

    def check(self, node: ast.AST) -> List[Issue]:
        issues = []
        # Your logic here
        return issues
```

---

## 📚 Further Reading

- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [Python Packaging Guide](https://packaging.python.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [argparse Tutorial](https://docs.python.org/3/howto/argparse.html)
