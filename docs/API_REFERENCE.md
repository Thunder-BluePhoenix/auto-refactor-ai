# API Reference

Complete reference for Auto Refactor AI code.

---

## 📦 Module: `auto_refactor_ai.analyzer`

Core analysis functionality.

---

### Class: `FunctionIssue`

**Type:** `dataclass`

Represents a single code quality issue detected in a function.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `file` | `str` | Path to the file containing the issue |
| `function_name` | `str` | Name of the function with the issue |
| `start_line` | `int` | Line number where the function starts |
| `end_line` | `int` | Line number where the function ends |
| `length` | `int` | Total number of lines in the function |
| `message` | `str` | Human-readable description of the issue |

#### Example

```python
issue = FunctionIssue(
    file="my_app/service.py",
    function_name="process_order",
    start_line=10,
    end_line=75,
    length=66,
    message="Function 'process_order' is 66 lines long. Consider splitting..."
)

print(f"{issue.function_name} at line {issue.start_line}")
# Output: process_order at line 10
```

---

### Function: `analyze_file`

Analyzes a Python file for code quality issues.

#### Signature

```python
def analyze_file(
    path: str,
    max_function_length: int = 30
) -> List[FunctionIssue]
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | *required* | Absolute or relative path to Python file |
| `max_function_length` | `int` | `30` | Maximum allowed function length in lines |

#### Returns

`List[FunctionIssue]` - List of issues found. Empty list if no issues or on parse error.

#### Raises

Does not raise exceptions. Parse errors are caught and logged to console.

#### Behavior

1. Reads file from disk with UTF-8 encoding
2. Parses source code into Abstract Syntax Tree (AST)
3. Walks AST to find all `FunctionDef` nodes
4. Checks each function's length against threshold
5. Creates `FunctionIssue` for violations
6. Returns all issues found

#### Edge Cases

- **Invalid Python syntax**: Prints error message, returns empty list
- **Non-existent file**: Raises `FileNotFoundError`
- **Binary file**: Raises `UnicodeDecodeError`
- **Empty file**: Returns empty list
- **No functions**: Returns empty list

#### Example

```python
from auto_refactor_ai.analyzer import analyze_file

# Basic usage
issues = analyze_file("my_script.py")

# Custom threshold
issues = analyze_file("my_script.py", max_function_length=50)

# Process results
for issue in issues:
    print(f"{issue.function_name}: {issue.length} lines")
```

#### Implementation Details

**AST Nodes Detected:**
- `ast.FunctionDef` - Regular function definitions
- Uses `node.lineno` and `node.end_lineno` for line tracking
- Falls back to `getattr(node, "end_lineno", start)` for Python < 3.8

**Performance:**
- O(n) where n is number of AST nodes
- Typically < 100ms for files under 1000 lines

---

## 📦 Module: `auto_refactor_ai.cli`

Command-line interface functionality.

---

### Function: `main`

Main entry point for the CLI application.

#### Signature

```python
def main() -> None
```

#### Behavior

1. Creates argument parser
2. Parses command-line arguments
3. Validates input path
4. Routes to appropriate handler based on path type

#### Arguments Parsed

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `path` | positional | Yes | - | File or directory to analyze |
| `--max-len` | optional | No | `30` | Max function length threshold |

#### Exit Codes

- `0` - Success
- `1` - Error (file not found, parse error, etc.)

#### Example Usage

```bash
# Analyze single file
python -m auto_refactor_ai script.py

# Analyze directory
python -m auto_refactor_ai src/

# Custom threshold
python -m auto_refactor_ai . --max-len 50
```

---

### Function: `analyze_single_file`

Analyzes a single Python file and prints results.

#### Signature

```python
def analyze_single_file(path: Path, max_len: int) -> None
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `Path` | Path object pointing to Python file |
| `max_len` | `int` | Maximum function length threshold |

#### Behavior

1. Converts `Path` to string
2. Calls `analyze_file()`
3. Passes results to `print_issues()`

#### Example

```python
from pathlib import Path
from auto_refactor_ai.cli import analyze_single_file

analyze_single_file(Path("script.py"), max_len=25)
```

---

### Function: `analyze_directory`

Recursively analyzes all Python files in a directory.

#### Signature

```python
def analyze_directory(root: Path, max_len: int) -> None
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `root` | `Path` | Root directory to search |
| `max_len` | `int` | Maximum function length threshold |

#### Behavior

1. Uses `Path.rglob("*.py")` to find all Python files recursively
2. Filters hidden directories (starting with `.`)
3. Analyzes each file independently
4. Prints results for each file

#### Example

```python
from pathlib import Path
from auto_refactor_ai.cli import analyze_directory

analyze_directory(Path("my_project/"), max_len=30)
```

---

### Function: `print_issues`

Formats and prints issues to console.

#### Signature

```python
def print_issues(issues: List[FunctionIssue]) -> None
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `issues` | `List[FunctionIssue]` | Issues to display |

#### Behavior

- Returns immediately if list is empty
- Prints each issue with formatted output
- Uses multi-line format for readability

#### Output Format

```
[LONG FUNCTION] path/to/file.py:10-75
  - Function : function_name
  - Length   : 66 lines
  - Suggestion: [detailed message]
```

#### Example

```python
from auto_refactor_ai.cli import print_issues
from auto_refactor_ai.analyzer import analyze_file

issues = analyze_file("script.py")
print_issues(issues)
```

---

## 🔧 Internal Implementation Details

### AST Processing

**Function Detection Algorithm:**

```python
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        # Process function
```

**Line Counting:**

```python
length = end_lineno - lineno + 1
# +1 because line numbers are inclusive
```

**Example:**
- Function starts at line 10
- Function ends at line 20
- Length = 20 - 10 + 1 = 11 lines

---

### File Discovery

**Directory Scanning:**

```python
python_files = list(root.rglob("*.py"))
```

**Pattern:** `**/*.py` matches all `.py` files recursively

**Excluded:**
- Hidden files (`.hidden.py`)
- Files in hidden directories (`.venv/`, `.git/`)

---

## 📝 Type Hints

All functions include complete type hints for IDE support.

**Import types:**
```python
from typing import List
from pathlib import Path
from dataclasses import dataclass
```

**Function signatures:**
```python
def analyze_file(path: str, max_function_length: int = 30) -> List[FunctionIssue]:
    ...
```

---

## 🧪 Testing Utilities

### Creating Test Files

```python
import pytest
from pathlib import Path

@pytest.fixture
def temp_python_file(tmp_path: Path) -> Path:
    """Create a temporary Python file for testing."""
    file = tmp_path / "test.py"
    file.write_text("""
def example_function():
    pass
""")
    return file

def test_analysis(temp_python_file):
    from auto_refactor_ai.analyzer import analyze_file
    issues = analyze_file(str(temp_python_file))
    assert isinstance(issues, list)
```

---

## 🔮 Future API (V1+)

### Class: `Rule` (V1)

**Status:** Planned

```python
from abc import ABC, abstractmethod

class Rule(ABC):
    @abstractmethod
    def check(self, node: ast.AST) -> List[Issue]:
        """Check AST node and return issues."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Rule identifier."""
        pass

    @property
    def severity(self) -> str:
        """Issue severity level."""
        return "WARN"
```

---

### Class: `Config` (V2)

**Status:** Planned

```python
class Config:
    def __init__(self, config_path: Optional[Path] = None):
        self.rules: Dict[str, Any] = {}
        self.output: Dict[str, Any] = {}

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load config from TOML file."""
        ...

    def get_rule_config(self, rule_name: str) -> Dict[str, Any]:
        """Get configuration for specific rule."""
        ...
```

---

### Function: `analyze_with_rules` (V1)

**Status:** Planned

```python
def analyze_with_rules(
    path: str,
    rules: List[Rule],
    config: Optional[Config] = None
) -> List[Issue]:
    """Analyze file using custom rule set."""
    ...
```

---

### Class: `LLMProvider` (V6) ✅

**Status:** Complete

**Module:** `auto_refactor_ai.llm_providers`

```python
class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
```

---

### Class: `LLMConfig` (V6) ✅

**Status:** Complete

**Module:** `auto_refactor_ai.llm_providers`

```python
@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 2000
    timeout: int = 60

    @classmethod
    def from_env(cls, provider: LLMProvider = LLMProvider.OPENAI) -> "LLMConfig":
        """Create config from environment variables."""
        ...
```

---

### Class: `BaseLLMProvider` (V6) ✅

**Status:** Complete

**Module:** `auto_refactor_ai.llm_providers`

```python
class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, config: LLMConfig): ...

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response from the LLM."""
        ...

    def is_available(self) -> bool:
        """Check if the provider is configured and available."""
        ...

    def get_refactoring_suggestion(
        self,
        code: str,
        issue_type: str,
        issue_message: str,
        function_name: str
    ) -> RefactoringSuggestion:
        """Generate a refactoring suggestion for the given code."""
        ...
```

**Implementations:** `OpenAIProvider`, `AnthropicProvider`, `GoogleProvider`, `OllamaProvider`

---

### Function: `get_provider` (V6) ✅

**Status:** Complete

**Module:** `auto_refactor_ai.llm_providers`

```python
def get_provider(config: LLMConfig) -> BaseLLMProvider:
    """Factory function to get appropriate provider based on config."""
    ...
```

---

### Function: `check_provider_availability` (V6) ✅

**Status:** Complete

**Module:** `auto_refactor_ai.llm_providers`

```python
def check_provider_availability() -> Dict[str, bool]:
    """Check which providers are available based on API keys and packages."""
    ...
```

---

## 🤖 Module: `auto_refactor_ai.ai_suggestions` (V6) ✅

AI-powered code refactoring suggestions.

---

### Function: `extract_function_source`

```python
def extract_function_source(
    file_path: str,
    start_line: int,
    end_line: int
) -> str:
    """Extract function source code from a file."""
    ...
```

---

### Function: `get_ai_suggestions`

```python
def get_ai_suggestions(
    issues: List[Issue],
    config: Optional[LLMConfig] = None,
    max_issues: int = 5,
    skip_info: bool = True,
) -> AIAnalysisSummary:
    """Get AI suggestions for a list of issues."""
    ...
```

---

### Function: `format_ai_suggestion`

```python
def format_ai_suggestion(
    result: AIAnalysisResult,
    show_original: bool = True
) -> str:
    """Format an AI suggestion for display."""
    ...
```

---

### Function: `print_ai_suggestions`

```python
def print_ai_suggestions(
    summary: AIAnalysisSummary,
    show_original: bool = True
) -> None:
    """Print all AI suggestions to stdout."""
    ...
```

---

### Class: `AIAnalysisResult`

```python
@dataclass
class AIAnalysisResult:
    """Result of AI analysis for a single issue."""
    issue: Issue
    suggestion: RefactoringSuggestion
    original_function_code: str
    tokens_used: int = 0
    cost_estimate: float = 0.0
```

---

### Class: `AIAnalysisSummary`

```python
@dataclass
class AIAnalysisSummary:
    """Summary of AI analysis for all issues."""
    results: List[AIAnalysisResult]
    total_tokens: int = 0
    total_cost: float = 0.0
    provider: str = ""
    model: str = ""
    errors: List[str]

    @property
    def success_count(self) -> int: ...

    @property
    def error_count(self) -> int: ...
```

---

## 🔧 Module: `auto_refactor_ai.auto_refactor` (V7) ✅

Auto-refactor functionality for applying AI suggestions.

---

### Class: `RefactorResult`

```python
@dataclass
class RefactorResult:
    """Result of a single refactoring operation."""
    file_path: str
    function_name: str
    original_code: str
    refactored_code: str
    start_line: int
    end_line: int
    backup_path: Optional[str] = None
    diff: str = ""
    applied: bool = False
    skipped: bool = False
    error: Optional[str] = None
```

---

### Class: `RefactorSummary`

```python
@dataclass
class RefactorSummary:
    """Summary of all refactoring operations."""
    results: List[RefactorResult]
    backup_dir: Optional[str]
    dry_run: bool

    @property
    def total_count(self) -> int: ...
    @property
    def applied_count(self) -> int: ...
    @property
    def skipped_count(self) -> int: ...
    @property
    def error_count(self) -> int: ...
```

---

### Function: `generate_diff`

```python
def generate_diff(
    original: str,
    refactored: str,
    file_path: str = "file.py",
    context_lines: int = 3
) -> str:
    """Generate a unified diff between original and refactored code."""
    ...
```

---

### Function: `create_backup`

```python
def create_backup(file_path: str, backup_dir: str) -> str:
    """Create a backup of a file before modification."""
    ...
```

---

### Function: `apply_refactoring`

```python
def apply_refactoring(
    file_path: str,
    original_function: str,
    refactored_code: str,
    start_line: int,
    end_line: int
) -> Tuple[bool, Optional[str]]:
    """Apply refactored code to a file."""
    ...
```

---

### Function: `rollback_file`

```python
def rollback_file(
    file_path: str,
    backup_path: str
) -> Tuple[bool, Optional[str]]:
    """Rollback a file to its backup version."""
    ...
```

---

### Function: `auto_refactor`

```python
def auto_refactor(
    ai_summary: AIAnalysisSummary,
    dry_run: bool = True,
    interactive: bool = False,
    backup_dir: str = ".auto-refactor-backup",
    create_backups: bool = True,
) -> RefactorSummary:
    """Apply AI suggestions to refactor code."""
    ...
```

---

---

## 📦 Module: `auto_refactor_ai.project_analyzer` (V8)

**Added in V8 (0.8.0)**

Project-level analysis module for detecting cross-file patterns and duplicates.

### Class: `FunctionSignature`

```python
@dataclass
class FunctionSignature:
    file: str           # Path to the file
    name: str           # Function name
    start_line: int     # Start line number
    end_line: int       # End line number
    parameters: List[str] # List of parameter names
    body_hash: str      # MD5 hash of normalized AST
    parameter_count: int
    line_count: int

    @property
    def location(self) -> str: ...
    @property
    def qualified_name(self) -> str: ...
```

---

### Class: `DuplicateGroup`

```python
@dataclass
class DuplicateGroup:
    functions: List[FunctionSignature]
    similarity: float       # 0.0 to 1.0
    suggested_name: str     # Suggested name for consolidated function
    suggested_module: str   # Suggested module path for extraction

    @property
    def count(self) -> int: ...
    @property
    def files(self) -> Set[str]: ...
    @property
    def potential_savings(self) -> int: ...
```

---

### Class: `ProjectAnalysis`

```python
@dataclass
class ProjectAnalysis:
    root_path: str
    files_analyzed: int
    functions_found: int
    duplicates: List[DuplicateGroup]
    recommendations: List[str]
```

---

### Function: `find_duplicates`

```python
def find_duplicates(
    functions: List[FunctionSignature],
    threshold: float = 0.8,
    min_lines: int = 5
) -> List[DuplicateGroup]:
    """Find duplicate/similar functions in a list of signatures."""
    ...
```

---

### Function: `analyze_project`

```python
def analyze_project(
    root_path: str,
    min_lines: int = 5,
    similarity_threshold: float = 0.8
) -> ProjectAnalysis:
    """Analyze a project directory for duplicates and patterns."""
    ...
```

---

## 📊 Constants

```python
# Default values
DEFAULT_MAX_FUNCTION_LENGTH = 30
DEFAULT_MAX_PARAMETERS = 5  # V1+
DEFAULT_MAX_NESTING = 3     # V1+

# Severity levels (V1+)
SEVERITY_INFO = "INFO"
SEVERITY_WARN = "WARN"
SEVERITY_CRITICAL = "CRITICAL"

# Output formats (V2+)
FORMAT_TEXT = "text"
FORMAT_JSON = "json"
```

---

## 🎯 Best Practices

### Using the API

**DO:**
```python
# Use Path objects for file paths
from pathlib import Path
issues = analyze_file(str(Path("script.py")))

# Check return value
if issues:
    print(f"Found {len(issues)} issues")

# Handle errors gracefully
try:
    issues = analyze_file("script.py")
except FileNotFoundError:
    print("File not found")
```

**DON'T:**
```python
# Don't ignore return value
analyze_file("script.py")  # Issues are lost!

# Don't assume file exists
issues = analyze_file("maybe_exists.py")  # May crash

# Don't hardcode paths
issues = analyze_file("C:\\Users\\Me\\script.py")  # Not portable
```

---

## 🔍 Debugging

### Enable Verbose Output

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect AST

```python
import ast

code = open("script.py").read()
tree = ast.parse(code)
print(ast.dump(tree, indent=2))
```

### Profile Performance

```python
import time

start = time.time()
issues = analyze_file("large_file.py")
print(f"Analysis took {time.time() - start:.2f}s")
```

---

## 📚 See Also

- [Architecture Guide](ARCHITECTURE.md) - System design
- [Learning Guide](LEARNING_GUIDE.md) - Educational resources
- [Roadmap](ROADMAP.md) - Future features

---

## 🤝 Contributing

API additions and improvements welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md).

**Guidelines:**
- Maintain backward compatibility
- Add type hints
- Include docstrings
- Write tests
- Update this reference
