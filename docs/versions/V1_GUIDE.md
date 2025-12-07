# V1 Implementation Guide

## Overview

V1 builds on V0 by adding **multiple analysis rules**, **severity levels**, and **improved output formatting**. This guide walks you through the implementation step-by-step.

## What You'll Learn

- Advanced AST manipulation
- AST Visitor pattern
- Enums and dataclasses
- Rule-based architecture
- Severity classification logic
- Code quality theory

## Prerequisites

- Completed V0 (basic analyzer with single rule)
- Understanding of Python AST basics
- Familiarity with dataclasses

## Implementation Steps

### Step 1: Add Severity Levels

First, we add an Enum for severity levels:

```python
from enum import Enum

class Severity(Enum):
    """Severity levels for code issues."""
    INFO = "INFO"
    WARN = "WARN"
    CRITICAL = "CRITICAL"
```

**Why Enums?**
- Type-safe constants
- Better than string literals
- IDE autocomplete support
- Prevents typos

### Step 2: Enhance the Issue Dataclass

Update the `FunctionIssue` to a more generic `Issue` class:

```python
@dataclass
class Issue:
    """Represents a code quality issue found during analysis."""
    severity: Severity
    file: str
    function_name: str
    start_line: int
    end_line: int
    rule_name: str  # NEW: Identifies which rule triggered
    message: str
    details: dict = None  # NEW: Optional metadata
```

**Key Changes:**
- Added `severity` field
- Added `rule_name` to identify which rule was violated
- Added `details` dict for rule-specific metadata

### Step 3: Implement Rule 2 - Too Many Parameters

Create a function to check parameter count:

```python
def check_too_many_parameters(node: ast.FunctionDef, path: str, max_params: int = 5) -> Issue:
    """Rule 2: Check if function has too many parameters."""
    start = node.lineno
    end = getattr(node, "end_lineno", start)

    # Count all parameters (args, kwargs, kwonly, etc.)
    param_count = (
        len(node.args.args) +
        len(node.args.kwonlyargs) +
        (1 if node.args.vararg else 0) +
        (1 if node.args.kwarg else 0)
    )

    if param_count > max_params:
        # Determine severity
        if param_count > max_params * 2:
            severity = Severity.CRITICAL
        elif param_count > max_params * 1.5:
            severity = Severity.WARN
        else:
            severity = Severity.INFO

        message = (
            f"Function '{node.name}' has {param_count} parameters (recommended: ≤ {max_params}). "
            f"Consider grouping related parameters into a dataclass or config object."
        )

        return Issue(
            severity=severity,
            file=path,
            function_name=node.name,
            start_line=start,
            end_line=end,
            rule_name="too-many-parameters",
            message=message,
            details={"param_count": param_count, "max_params": max_params}
        )
    return None
```

**Key Concepts:**
- `node.args.args`: Regular positional parameters
- `node.args.kwonlyargs`: Keyword-only parameters
- `node.args.vararg`: The `*args` parameter
- `node.args.kwarg`: The `**kwargs` parameter

### Step 4: Implement Rule 3 - Deep Nesting (AST Visitor Pattern)

For nesting detection, we need to use the **Visitor Pattern**:

```python
class NestingVisitor(ast.NodeVisitor):
    """Visitor to calculate maximum nesting depth in a function."""

    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0

    def visit_If(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)  # Visit children
        self.current_depth -= 1

    def visit_For(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_With(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
```

**Visitor Pattern Explained:**
- `NodeVisitor` is a base class that walks the AST
- Override `visit_<NodeType>` methods for specific nodes
- `self.generic_visit(node)` recursively visits children
- We track depth by incrementing on entry, decrementing on exit

Now use the visitor in the rule:

```python
def check_deep_nesting(node: ast.FunctionDef, path: str, max_depth: int = 3) -> Issue:
    """Rule 3: Check if function has too much nesting."""
    start = node.lineno
    end = getattr(node, "end_lineno", start)

    # Calculate nesting depth
    visitor = NestingVisitor()
    visitor.visit(node)
    depth = visitor.max_depth

    if depth > max_depth:
        # Determine severity
        if depth > max_depth * 2:
            severity = Severity.CRITICAL
        elif depth > max_depth * 1.5:
            severity = Severity.WARN
        else:
            severity = Severity.INFO

        message = (
            f"Function '{node.name}' has {depth} levels of nesting (max: {max_depth}). "
            f"High nesting makes code harder to understand. Consider extracting nested logic into helper functions."
        )

        return Issue(
            severity=severity,
            file=path,
            function_name=node.name,
            start_line=start,
            end_line=end,
            rule_name="deep-nesting",
            message=message,
            details={"nesting_depth": depth, "max_depth": max_depth}
        )
    return None
```

### Step 5: Update the Main Analyzer

Refactor `analyze_file()` to apply all rules:

```python
def analyze_file(
    path: str,
    max_function_length: int = 30,
    max_parameters: int = 5,
    max_nesting_depth: int = 3
) -> List[Issue]:
    """Analyze a Python file and return a list of code quality issues."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"[ERROR] Cannot read {path}: {e}")
        return []

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as e:
        print(f"[ERROR] Cannot parse {path}: {e}")
        return []

    issues: List[Issue] = []

    # Apply all rules to each function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Rule 1: Function length
            issue = check_function_length(node, path, max_function_length)
            if issue:
                issues.append(issue)

            # Rule 2: Too many parameters
            issue = check_too_many_parameters(node, path, max_parameters)
            if issue:
                issues.append(issue)

            # Rule 3: Deep nesting
            issue = check_deep_nesting(node, path, max_nesting_depth)
            if issue:
                issues.append(issue)

    return issues
```

### Step 6: Update CLI Output

Add sorting and summary:

```python
def print_issues(issues):
    """Print issues grouped by severity."""
    if not issues:
        print("\n✓ No issues found! Your code looks good.\n")
        return

    # Sort by severity (CRITICAL > WARN > INFO) then by file
    severity_order = {Severity.CRITICAL: 0, Severity.WARN: 1, Severity.INFO: 2}
    sorted_issues = sorted(
        issues,
        key=lambda x: (severity_order[x.severity], x.file, x.start_line)
    )

    for issue in sorted_issues:
        severity_label = f"[{issue.severity.value}]"
        print(
            f"\n{severity_label} {issue.file}:{issue.start_line}-{issue.end_line}  {issue.function_name}()"
        )
        print(f"  - {issue.message}")


def print_summary(issues):
    """Print a summary of issues by severity."""
    if not issues:
        return

    critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
    warn_count = sum(1 for i in issues if i.severity == Severity.WARN)
    info_count = sum(1 for i in issues if i.severity == Severity.INFO)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  CRITICAL: {critical_count}")
    print(f"  WARN:     {warn_count}")
    print(f"  INFO:     {info_count}")
    print(f"  TOTAL:    {len(issues)}")
    print("=" * 60 + "\n")
```

### Step 7: Add CLI Arguments

Update argument parser:

```python
parser.add_argument(
    "--max-params",
    type=int,
    default=5,
    help="Maximum allowed parameters per function. Default: 5",
)
parser.add_argument(
    "--max-nesting",
    type=int,
    default=3,
    help="Maximum allowed nesting depth. Default: 3",
)
```

## Testing V1

Create comprehensive test files:

```python
# test_parameter_issues.py
def six_params(a, b, c, d, e, f):
    """INFO: 6 parameters (1.2x over limit of 5)."""
    return a + b + c + d + e + f

def eight_params(a, b, c, d, e, f, g, h):
    """WARN: 8 parameters (1.6x over limit)."""
    return a + b + c + d + e + f + g + h

def twelve_params(a, b, c, d, e, f, g, h, i, j, k, l):
    """CRITICAL: 12 parameters (2.4x over limit)."""
    return sum([a, b, c, d, e, f, g, h, i, j, k, l])
```

Run tests:
```bash
python -m auto_refactor_ai test_files/test_parameter_issues.py
python -m auto_refactor_ai test_files/test_nesting_issues.py
python -m auto_refactor_ai test_files/
```

## Architecture Insights

### Why Separate Rule Functions?

```python
# ✅ Good: Separate functions
def check_function_length(...): ...
def check_too_many_parameters(...): ...
def check_deep_nesting(...): ...

# ❌ Bad: One giant function
def check_all_rules(...):
    # 200 lines of mixed logic
```

**Benefits:**
- Single Responsibility Principle
- Easy to add new rules
- Easy to disable specific rules
- Better testability

### Severity Classification Pattern

All rules follow this pattern:

```python
if violation:
    if violation > threshold * 2:
        severity = Severity.CRITICAL
    elif violation > threshold * 1.5:
        severity = Severity.WARN
    else:
        severity = Severity.INFO
```

This provides consistent, predictable behavior across all rules.

## Common Pitfalls

### 1. Forgetting to Count All Parameter Types

```python
# ❌ Wrong: Only counts regular args
param_count = len(node.args.args)

# ✅ Correct: Counts all parameter types
param_count = (
    len(node.args.args) +
    len(node.args.kwonlyargs) +
    (1 if node.args.vararg else 0) +
    (1 if node.args.kwarg else 0)
)
```

### 2. Not Restoring Depth in Visitor

```python
# ❌ Wrong: Depth keeps increasing
def visit_If(self, node):
    self.current_depth += 1
    self.generic_visit(node)
    # Missing: self.current_depth -= 1

# ✅ Correct: Properly restore depth
def visit_If(self, node):
    self.current_depth += 1
    self.generic_visit(node)
    self.current_depth -= 1  # ✅ Restore on exit
```

### 3. Wrong Severity Order

```python
# ❌ Wrong: INFO appears before CRITICAL
issues.sort(key=lambda x: x.severity.value)  # Alphabetical!

# ✅ Correct: Define explicit order
severity_order = {Severity.CRITICAL: 0, Severity.WARN: 1, Severity.INFO: 2}
issues.sort(key=lambda x: severity_order[x.severity])
```

## Exercises

1. **Add Rule 4**: Detect functions with no docstring
2. **Enhance nesting detection**: Count `try/except` blocks
3. **Add filtering**: Allow users to disable specific rules via CLI
4. **Improve messages**: Add code examples to suggestions

## Next Steps

In V2, we'll add:
- Configuration file support (TOML/YAML)
- JSON output mode for tooling integration
- More flexible rule management

## Key Takeaways

✅ **AST Visitor Pattern** is powerful for tree traversal
✅ **Enums** provide type-safe constants
✅ **Severity levels** help prioritize fixes
✅ **Rule-based architecture** enables easy extension
✅ **Consistent patterns** make code maintainable
