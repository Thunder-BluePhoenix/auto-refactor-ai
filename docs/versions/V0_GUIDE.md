# V0 Implementation Guide

Complete walkthrough of building the V0 static analyzer.

---

## 🎯 Goal

Build a simple Python file analyzer that detects long functions.

**What it does:**
- Scan Python file(s)
- Find functions longer than N lines
- Print human-readable suggestions

**What it doesn't do (yet):**
- Multiple rule types (V1)
- Config files (V2)
- AI suggestions (V6)
- Auto-fix (V7)

---

## 📋 Prerequisites

- Python 3.8 or higher
- Basic understanding of Python
- Text editor or IDE
- Terminal/command prompt

---

## 🏗️ Step-by-Step Implementation

### Step 1: Project Setup

Create the directory structure:

```bash
mkdir auto-refactor-ai
cd auto-refactor-ai
mkdir auto_refactor_ai
```

Create these files:
```
auto-refactor-ai/
├── auto_refactor_ai/
│   ├── __init__.py
│   ├── __main__.py
│   ├── analyzer.py
│   └── cli.py
├── pyproject.toml
├── README.md
└── sample_test.py
```

---

### Step 2: Implement `analyzer.py`

This is the core logic.

**File: `auto_refactor_ai/analyzer.py`**

```python
import ast
from dataclasses import dataclass
from typing import List


@dataclass
class FunctionIssue:
    """Represents a code quality issue in a function."""
    file: str
    function_name: str
    start_line: int
    end_line: int
    length: int
    message: str


def analyze_file(path: str, max_function_length: int = 30) -> List[FunctionIssue]:
    """
    Analyze a Python file for long functions.

    Args:
        path: Path to the Python file
        max_function_length: Maximum allowed function length

    Returns:
        List of FunctionIssue objects
    """
    # Read the file
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    # Parse into AST
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as e:
        print(f"[ERROR] Cannot parse {path}: {e}")
        return []

    issues: List[FunctionIssue] = []

    # Walk the AST to find functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            end = getattr(node, "end_lineno", start)  # Python 3.8+
            length = end - start + 1

            # Check if function is too long
            if length > max_function_length:
                message = (
                    f"Function '{node.name}' in {path} is {length} lines long. "
                    f"Consider splitting it into smaller functions with single responsibilities."
                )
                issues.append(
                    FunctionIssue(
                        file=path,
                        function_name=node.name,
                        start_line=start,
                        end_line=end,
                        length=length,
                        message=message,
                    )
                )

    return issues
```

**Key Concepts:**

1. **Dataclass for Issues**
   - Clean, type-safe data structure
   - Auto-generates `__init__`, `__repr__`, etc.

2. **AST Parsing**
   ```python
   tree = ast.parse(source, filename=path)
   ```
   - Converts Python source code to tree structure
   - Raises `SyntaxError` on invalid Python

3. **Walking the AST**
   ```python
   for node in ast.walk(tree):
   ```
   - Visits every node in the tree
   - No specific order guaranteed

4. **Function Detection**
   ```python
   if isinstance(node, ast.FunctionDef):
   ```
   - `FunctionDef` = regular function
   - Doesn't catch `AsyncFunctionDef` (async functions)

5. **Line Numbers**
   ```python
   start = node.lineno
   end = getattr(node, "end_lineno", start)
   ```
   - `lineno` = starting line (always available)
   - `end_lineno` = ending line (Python 3.8+)
   - Fallback for older Python versions

---

### Step 3: Implement `cli.py`

The command-line interface.

**File: `auto_refactor_ai/cli.py`**

```python
import argparse
from pathlib import Path

from .analyzer import analyze_file


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Auto Refactor AI – basic static analyzer (V0)"
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyze",
    )
    parser.add_argument(
        "--max-len",
        type=int,
        default=30,
        help="Maximum allowed function length (in lines). Default: 30",
    )

    args = parser.parse_args()
    target_path = Path(args.path)

    # Route to appropriate handler
    if target_path.is_file():
        analyze_single_file(target_path, args.max_len)
    elif target_path.is_dir():
        analyze_directory(target_path, args.max_len)
    else:
        print(f"[ERROR] Path not found: {target_path}")


def analyze_single_file(path: Path, max_len: int):
    """Analyze a single Python file."""
    issues = analyze_file(str(path), max_function_length=max_len)
    print_issues(issues)


def analyze_directory(root: Path, max_len: int):
    """Recursively analyze all Python files in directory."""
    python_files = list(root.rglob("*.py"))

    if not python_files:
        print("[INFO] No Python files found.")
        return

    for file in python_files:
        issues = analyze_file(str(file), max_function_length=max_len)
        print_issues(issues)


def print_issues(issues):
    """Format and print issues to console."""
    if not issues:
        return

    for issue in issues:
        print(
            f"\n[LONG FUNCTION] {issue.file}:{issue.start_line}-{issue.end_line}\n"
            f"  - Function : {issue.function_name}\n"
            f"  - Length   : {issue.length} lines\n"
            f"  - Suggestion: {issue.message}\n"
        )


if __name__ == "__main__":
    main()
```

**Key Concepts:**

1. **Argument Parsing**
   ```python
   parser.add_argument("path", help="...")
   parser.add_argument("--max-len", type=int, default=30)
   ```
   - Positional argument: `path` (required)
   - Optional argument: `--max-len` (has default)

2. **Path Handling**
   ```python
   target_path = Path(args.path)
   if target_path.is_file():
       ...
   elif target_path.is_dir():
       ...
   ```
   - `pathlib.Path` for cross-platform compatibility
   - Check if file or directory

3. **Recursive File Discovery**
   ```python
   python_files = list(root.rglob("*.py"))
   ```
   - `rglob()` = recursive glob
   - Finds all `.py` files in subdirectories

4. **Output Formatting**
   - Multi-line format for readability
   - Shows file, function, line numbers, suggestion

---

### Step 4: Package Entry Points

**File: `auto_refactor_ai/__init__.py`**

```python
from .cli import main

__all__ = ["main"]
```

**File: `auto_refactor_ai/__main__.py`**

```python
from .cli import main

if __name__ == "__main__":
    main()
```

**Purpose:**
- `__init__.py` exports `main()` for package imports
- `__main__.py` enables `python -m auto_refactor_ai`

---

### Step 5: Package Metadata

**File: `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "auto-refactor-ai"
version = "0.1.0"
description = "A beginner-friendly static analyzer for Python code refactoring suggestions"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
keywords = ["refactoring", "static-analysis", "code-quality", "linting"]
authors = [
    {name = "Your Name"}
]

[project.scripts]
auto-refactor-ai = "auto_refactor_ai:main"
```

**Key Fields:**
- `name` - Package name on PyPI
- `version` - Semantic versioning (MAJOR.MINOR.PATCH)
- `requires-python` - Minimum Python version
- `project.scripts` - CLI command name

---

### Step 6: Create Test File

**File: `sample_test.py`**

```python
"""Sample file with long functions to test the analyzer."""


def short_function():
    """This is a short function that should not be flagged."""
    x = 1
    y = 2
    return x + y


def very_long_function(data):
    """This function is intentionally long to trigger the analyzer."""
    result = []

    for item in data:
        if item > 0:
            processed = item * 2
            if processed > 100:
                processed = 100
            result.append(processed)
        elif item < 0:
            processed = abs(item)
            result.append(processed)
        else:
            result.append(0)

    total = sum(result)
    average = total / len(result) if result else 0
    maximum = max(result) if result else 0
    minimum = min(result) if result else 0

    stats = {
        'total': total,
        'average': average,
        'max': maximum,
        'min': minimum,
        'count': len(result)
    }

    return stats
```

---

## 🧪 Testing Your Implementation

### Test 1: Single File Analysis

```bash
cd auto-refactor-ai
python -m auto_refactor_ai sample_test.py
```

**Expected Output:**
```
[LONG FUNCTION] sample_test.py:11-58
  - Function : very_long_function
  - Length   : 48 lines
  - Suggestion: Function 'very_long_function' in sample_test.py is 48 lines long...
```

### Test 2: Custom Threshold

```bash
python -m auto_refactor_ai sample_test.py --max-len 5
```

**Expected:** Both functions flagged (since both > 5 lines)

### Test 3: Directory Analysis

```bash
python -m auto_refactor_ai .
```

**Expected:** Analyzes all `.py` files in current directory

### Test 4: Non-existent Path

```bash
python -m auto_refactor_ai nonexistent.py
```

**Expected:** Error message about path not found

---

## 🐛 Common Issues & Solutions

### Issue: `ModuleNotFoundError: No module named 'auto_refactor_ai'`

**Cause:** Running from wrong directory

**Solution:**
```bash
# Make sure you're in the auto-refactor-ai directory
cd auto-refactor-ai
python -m auto_refactor_ai sample_test.py
```

### Issue: `SyntaxError` when analyzing files

**Cause:** File contains invalid Python syntax

**Solution:** This is expected behavior. The analyzer will print an error and continue.

### Issue: No output when analyzing directory

**Cause:** No Python files found, or all functions are short

**Solution:** Check that directory contains `.py` files with long functions

---

## 🎓 Learning Exercises

### Exercise 1: Add Async Function Support

**Goal:** Also detect `async def` functions

**Hint:** Check for `ast.AsyncFunctionDef` in addition to `ast.FunctionDef`

<details>
<summary>Solution</summary>

```python
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        # ... rest of code
```
</details>

### Exercise 2: Count Total Functions

**Goal:** Print summary like "Analyzed 10 functions, found 3 issues"

**Hint:** Count all `FunctionDef` nodes, not just long ones

### Exercise 3: Add Quiet Mode

**Goal:** Add `--quiet` flag that only shows file names with issues

**Hint:** Modify `print_issues()` to accept a `quiet` parameter

---

## 🚀 Next Steps

Congratulations! You've built V0.

**What you've learned:**
- ✅ Python AST basics
- ✅ Building CLI tools with argparse
- ✅ Package structure
- ✅ File I/O and error handling
- ✅ Data classes

**Ready for more?**

Move to [V1](V1_GUIDE.md) to add:
- Multiple rule types
- Severity levels
- Better architecture

---

## 📚 Resources

- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [argparse Tutorial](https://docs.python.org/3/howto/argparse.html)
- [Dataclasses Guide](https://realpython.com/python-data-classes/)
- [Pathlib Guide](https://realpython.com/python-pathlib/)

---

## 🤝 Get Help

- Check [ARCHITECTURE.md](../ARCHITECTURE.md) for design details
- See [LEARNING_GUIDE.md](../LEARNING_GUIDE.md) for AST tutorials
- Ask questions in GitHub Discussions
