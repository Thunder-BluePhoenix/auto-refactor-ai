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
│   ├── analyzer.py            # Core analysis logic (V0-V4)
│   ├── cli.py                 # Command-line interface (V0-V6)
│   ├── config.py              # Configuration management (V2+)
│   ├── explanations.py        # Template-based explanations (V5)
│   ├── llm_providers.py       # LLM provider abstraction (V6)
│   ├── ai_suggestions.py      # AI-powered suggestions (V6)
│   ├── auto_refactor.py       # Auto-refactor with apply (V7)
│   ├── project_analyzer.py    # Project-level analysis (V8)
│   └── git_utils.py           # Git integration (V9)
│
├── tests/                     # Test suite (V4+) - 157 tests
│   ├── __init__.py           # Test package initialization
│   ├── test_analyzer.py      # 26 tests - Core analysis tests
│   ├── test_config.py        # 22 tests - Configuration tests
│   ├── test_cli.py           # 14 tests - CLI interface tests
│   ├── test_explanations.py  # 15 tests - Explanations tests (V5)
│   ├── test_llm_providers.py # 26 tests - LLM provider tests (V6)
│   ├── test_ai_suggestions.py # 10 tests - AI suggestions (V6)
│   ├── test_auto_refactor.py  # 18 tests - Auto-refactor (V7)
│   ├── test_project_analyzer.py # 18 tests - Project analysis (V8)
│   └── test_git_utils.py      # 6 tests - Git integration (V9)
│
├── test_files/               # Sample files for manual testing
│   ├── README.md             # Test files documentation
│   ├── test_perfect_code.py  # Examples of good code
│   ├── test_length_issues.py # Function length test cases
│   ├── test_parameter_issues.py
│   ├── test_nesting_issues.py
│   ├── test_combined_issues.py
│   └── test_edge_cases.py
│
├── docs/                      # Documentation
│   ├── README.md             # Documentation index
│   ├── ROADMAP.md            # Full version roadmap
│   ├── ARCHITECTURE.md       # This file
│   ├── LEARNING_GUIDE.md     # Educational content
│   ├── API_REFERENCE.md      # Code documentation
│   ├── PROJECT_OVERVIEW.md   # High-level overview
│   ├── PUBLISHING_GUIDE.md   # PyPI publishing guide
│   └── versions/             # Version-specific guides
│       ├── V0_GUIDE.md
│       ├── V1_GUIDE.md
│       ├── V2_GUIDE.md
│       ├── V3_GUIDE.md
│       ├── V4_GUIDE.md
│       ├── V5_GUIDE.md
│       ├── V6_GUIDE.md
│       ├── V7_GUIDE.md
│       ├── V8_GUIDE.md
│       └── V9_GUIDE.md
│
├── .github/                   # GitHub configuration (V4+)
│   └── workflows/
│       └── test.yml          # CI/CD pipeline
│
├── examples/                  # Example configurations (V2+)
│   ├── config-strict.toml
│   └── config-relaxed.toml
│
├── scripts/                   # Utility scripts (V3+)
│   └── verify_install.py     # Installation verification
│
├── .pre-commit-config.yaml   # Pre-commit hooks (V4+)
├── pyproject.toml            # Package metadata & all tool configs
├── CHANGELOG.md              # Version history
├── LICENSE                   # MIT License (V3+)
├── MANIFEST.in               # Distribution file control (V3+)
├── README.md                 # Main documentation
└── .gitignore               # Git ignore patterns
```

---

## 🏗️ Core Components

### Current Architecture (V9 - 0.9.0)

The project has evolved through nine major versions, each adding significant functionality while maintaining backward compatibility.

### 1. `analyzer.py` - The Analysis Engine

**Purpose:** Core analysis logic with multiple rules and severity levels.

**Key Classes (V1+):**

#### `Severity` (Enum)
Severity classification for issues.

```python
class Severity(Enum):
    INFO = "INFO"          # 1-1.5x over limit
    WARN = "WARN"          # 1.5-2x over limit
    CRITICAL = "CRITICAL"  # 2x+ over limit
```

#### `Issue` (dataclass)
Represents a single code issue (renamed from `FunctionIssue` in V1).

```python
@dataclass
class Issue:
    severity: Severity     # Issue severity level
    file: str              # Path to file
    function_name: str     # Name of the function
    start_line: int        # Starting line number
    end_line: int          # Ending line number
    rule_name: str         # Rule that detected this issue
    message: str           # Human-readable description
    details: dict = None   # Additional metadata

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON output."""
        return {
            "severity": self.severity.value,
            "file": self.file,
            "function_name": self.function_name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "rule_name": self.rule_name,
            "message": self.message,
            "details": self.details or {}
        }
```

#### `NestingVisitor` (ast.NodeVisitor)
AST visitor for calculating nesting depth.

```python
class NestingVisitor(ast.NodeVisitor):
    """Visitor to calculate maximum nesting depth in a function."""

    def __init__(self):
        self.current_depth = 0
        self.max_depth = 0

    def visit_If(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    # Similar for For, While, With, Try, etc.
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

### LLM Integration (V6) ✅

**Status:** Complete in v0.6.0

**Provider Abstraction (`llm_providers.py`):**
```python
class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"

@dataclass
class LLMConfig:
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 2000

@dataclass
class RefactoringSuggestion:
    original_code: str
    refactored_code: str
    explanation: str
    confidence: float = 0.0
    changes_summary: List[str]

class BaseLLMProvider(ABC):
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse: ...
    def get_refactoring_suggestion(self, code, issue_type, message, func_name) -> RefactoringSuggestion: ...
    def is_available(self) -> bool: ...

class OpenAIProvider(BaseLLMProvider): ...
class AnthropicProvider(BaseLLMProvider): ...
class GoogleProvider(BaseLLMProvider): ...
class OllamaProvider(BaseLLMProvider): ...

def get_provider(config: LLMConfig) -> BaseLLMProvider: ...
def check_provider_availability() -> Dict[str, bool]: ...
```

**AI Suggestions (`ai_suggestions.py`):**
```python
def extract_function_source(file_path: str, start_line: int, end_line: int) -> str: ...
def get_ai_suggestions(issues, config, max_issues=5, skip_info=True) -> AIAnalysisSummary: ...
def format_ai_suggestion(result: AIAnalysisResult, show_original=True) -> str: ...
def print_ai_suggestions(summary: AIAnalysisSummary) -> None: ...
def get_provider_status_message() -> str: ...
```

---

## 🧪 Testing Architecture (V9)

### Test Suite Overview

**Statistics:**
- **Total Tests:** 157
- **Coverage:** 80%+ (exceeds 80% requirement)
- **Test Modules:** 9 (analyzer, config, CLI, explanations, llm_providers, ai_suggestions, auto_refactor, project_analyzer, git_utils)
- **Test Classes:** 45+
- **CI/CD:** GitHub Actions on 15 combinations (3 OS × 5 Python versions)

**Test Structure:**
```
tests/
├── __init__.py                # Test package initialization
├── test_analyzer.py          # 26 tests - Core analysis engine
│   ├── TestSeverity          # Severity enum tests
│   ├── TestIssue             # Issue dataclass tests
│   ├── TestNestingVisitor    # AST visitor tests
│   ├── TestCheckFunctionLength
│   ├── TestCheckTooManyParameters
│   ├── TestCheckDeepNesting
│   └── TestAnalyzeFile       # Integration tests
│
├── test_config.py            # 22 tests - Configuration system
│   ├── TestConfig            # Config dataclass tests
│   ├── TestParseSimpleToml   # TOML parser tests
│   ├── TestLoadTomlConfig    # TOML file loading
│   ├── TestFindConfigFile    # Config discovery
│   └── TestLoadConfig        # Full integration
│
├── test_cli.py               # 14 tests - CLI interface
│   ├── TestPrintIssues       # Text output formatting
│   ├── TestPrintSummary      # Summary statistics
│   ├── TestPrintJson         # JSON output
│   └── TestMainCLI           # Full CLI integration
│
├── test_explanations.py      # 15 tests - V5 explanations
│   ├── TestGetExplanation
│   ├── TestFormatExplanation
│   ├── TestGetSeverityGuidance
│   └── TestExplanationContent
│
├── test_llm_providers.py     # 26 tests - V6 LLM providers
│   ├── TestLLMProvider       # Provider enum tests
│   ├── TestLLMConfig         # Configuration tests
│   ├── TestLLMResponse       # Response handling
│   ├── TestOpenAIProvider    # OpenAI integration
│   ├── TestAnthropicProvider # Anthropic integration
│   ├── TestGoogleProvider    # Google Gemini integration
│   ├── TestOllamaProvider    # Local Ollama integration
│   ├── TestGetProvider       # Factory pattern tests
│   ├── TestResponseParsing   # LLM response parsing
│   └── TestCheckProviderAvailability
│
└── test_ai_suggestions.py    # 10 tests - V6 AI suggestions
    ├── TestExtractFunctionSource
    ├── TestAIAnalysisResult
    ├── TestAIAnalysisSummary
    └── TestFormatAISuggestion
```

### Testing Patterns

**Arrange-Act-Assert Pattern:**
```python
def test_function_over_limit_critical(self):
    """Test function way over limit (CRITICAL)."""
    # Arrange - Create test code
    code = "def long():\n" + "    x = 1\n" * 68 + "    return x"

    # Act - Parse and analyze
    tree = ast.parse(code)
    func = tree.body[0]
    issue = check_function_length(func, "test.py", max_length=30)

    # Assert - Verify results
    assert issue is not None
    assert issue.severity == Severity.CRITICAL
    assert issue.details["actual_length"] == 70
```

**Fixture Usage:**
```python
@pytest.fixture
def temp_config_file():
    """Create temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("max_function_length = 40\n")
        f.flush()
        yield Path(f.name)
    Path(f.name).unlink()
```

**Mocking for CLI Tests:**
```python
def test_main_with_help(self):
    """Test running with --help flag."""
    with patch("sys.argv", ["auto-refactor-ai", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
```

### Coverage Report

```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
auto_refactor_ai/__init__.py       2      0   100%
auto_refactor_ai/__main__.py       1      1     0%   1
auto_refactor_ai/analyzer.py     110      2    98%   121, 158
auto_refactor_ai/cli.py           74      3    96%   60, 96-97
auto_refactor_ai/config.py       122     30    75%   55, 110, ...
------------------------------------------------------------
TOTAL                            309     36    88%
```

### CI/CD Pipeline

**GitHub Actions Workflow:** `.github/workflows/test.yml`

**Three Jobs:**

1. **Multi-Platform Tests**
   - Operating Systems: Ubuntu, Windows, macOS
   - Python Versions: 3.8, 3.9, 3.10, 3.11, 3.12
   - Total: 15 test combinations
   - Coverage reporting to Codecov

2. **Code Quality Checks**
   - Black: Code formatting verification
   - Ruff: Linting checks
   - Mypy: Static type checking

3. **Self-Analysis (Dogfooding)**
   - Runs auto-refactor-ai on its own codebase
   - Fails build if critical issues found
   - Demonstrates confidence in the tool

### Pre-commit Hooks

**Configuration:** `.pre-commit-config.yaml`

**Hooks Executed:**
1. **General File Checks** (trailing whitespace, EOF, YAML/TOML validation)
2. **Black** - Auto-format code
3. **Ruff** - Lint with auto-fixes
4. **Mypy** - Type checking
5. **Self-Analysis** - Run auto-refactor-ai on changed files
6. **Pytest** - Run test suite before commit

### Code Quality Configuration

All tools configured in `pyproject.toml`:

**Pytest:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--verbose",
    "--cov=auto_refactor_ai",
    "--cov-fail-under=80",
]
```

**Black:**
```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
```

**Ruff:**
```toml
[tool.ruff]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4"]
```

**Mypy:**
```toml
[tool.mypy]
python_version = "3.8"
check_untyped_defs = true
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

| Technology | Purpose | Introduced | Status |
|------------|---------|------------|--------|
| `ast` | Parse Python code | V0 | ✅ Active |
| `argparse` | CLI argument parsing | V0 | ✅ Active |
| `pathlib` | Path operations | V0 | ✅ Active |
| `dataclasses` | Data structures | V0 | ✅ Active |
| `enum` | Severity levels | V1 | ✅ Active |
| TOML parser (fallback) | Config file parsing | V2 | ✅ Active |
| `json` | JSON output & config | V2 | ✅ Active |
| `pytest` | Testing framework | V4 | ✅ Active |
| `pytest-cov` | Coverage reporting | V4 | ✅ Active |
| `black` | Code formatting | V4 | ✅ Active |
| `ruff` | Fast linting | V4 | ✅ Active |
| `mypy` | Type checking | V4 | ✅ Active |
| `pre-commit` | Git hooks | V4 | ✅ Active |
| `openai` | OpenAI LLM integration | V6 | ✅ Active |
| `anthropic` | Anthropic Claude integration | V6 | ✅ Active |
| `google-generativeai` | Google Gemini integration | V6 | ✅ Active |
| `difflib` | Generate patches | V7 | 📅 Planned |
| `gitpython` | Git integration | V9 | 📅 Planned |

**Zero Runtime Dependencies**: The core package uses only Python standard library. AI dependencies are optional (`pip install auto-refactor-ai[ai-all]`).

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
