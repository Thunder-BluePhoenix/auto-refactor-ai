# V8 Implementation Guide: Project-Level Analysis

## Overview

V8 adds cross-file analysis capabilities to Auto Refactor AI, enabling detection of duplicate code patterns across an entire project.

## Goals

1. Detect duplicate/similar functions across files
2. Normalize AST for structural comparison
3. Generate architecture recommendations
4. Suggest module consolidation

## New Features

### 1. `--project` Flag

Enable project-level analysis:

```bash
# Basic project analysis
auto-refactor-ai myproject/ --project

# Find duplicates specifically
auto-refactor-ai myproject/ --project --find-duplicates

# Custom settings
auto-refactor-ai myproject/ --project --min-lines 10 --similarity-threshold 0.9
```

### 2. Duplicate Detection

The analyzer uses AST hashing to find structurally identical functions:

```
================================================================================
🔍 PROJECT-LEVEL ANALYSIS
================================================================================
Root: myproject/
Files Analyzed: 15
Functions Found: 87
--------------------------------------------------------------------------------

🔄 DUPLICATE CODE DETECTED (2 groups):
----------------------------------------

Group 1: 100% Similar (3 functions)
  • auth/login.py:validate_user() [lines 10-25]
  • auth/register.py:check_user() [lines 15-30]
  • api/auth.py:verify_user() [lines 20-35]

  💡 Suggestion: Extract to auth/shared.py
     Potential savings: ~30 lines

Group 2: 100% Similar (2 functions)
  • utils/format.py:format_date() [lines 5-15]
  • helpers/dates.py:render_date() [lines 10-20]

  💡 Suggestion: Extract to utils/shared.py
     Potential savings: ~10 lines

📊 RECOMMENDATIONS:
  • Found 2 group(s) of duplicate code. Consolidating could save ~40 lines.

================================================================================
```

## New CLI Flags (V8)

| Flag | Description |
|------|-------------|
| `--project`, `-p` | Enable project-level analysis |
| `--find-duplicates` | Find duplicate/similar code |
| `--similarity-threshold` | Minimum similarity (0.0-1.0, default: 0.8) |
| `--min-lines` | Minimum function lines (default: 5) |

## Architecture

### New Module: `project_analyzer.py`

```python
@dataclass
class FunctionSignature:
    file: str
    name: str
    parameters: List[str]
    body_hash: str
    line_count: int

@dataclass
class DuplicateGroup:
    functions: List[FunctionSignature]
    similarity: float
    suggested_module: str
    potential_savings: int

@dataclass
class ProjectAnalysis:
    files_analyzed: int
    functions_found: int
    duplicates: List[DuplicateGroup]
    recommendations: List[str]

# Core functions
def normalize_ast(node) -> str
def hash_function_body(func_node) -> str
def find_duplicates(functions, threshold) -> List[DuplicateGroup]
def analyze_project(root_path, config) -> ProjectAnalysis
```

## How It Works

1. **Parse all Python files** in the project
2. **Extract function signatures** including AST
3. **Normalize AST** by replacing variable names with placeholders
4. **Hash normalized AST** using MD5
5. **Group by hash** to find exact duplicates
6. **Generate recommendations** based on findings

## Testing

### New Test File: `test_project_analyzer.py`

15 tests covering:
- AST normalization
- Function hashing
- Duplicate detection
- Project analysis
- Output formatting

### Running Tests

```bash
# Run all tests (146 tests)
pytest tests/ -v --no-cov

# Run only V8 tests
pytest tests/test_project_analyzer.py -v
```

## Learning Outcomes

1. **AST manipulation** - Normalizing code structure
2. **Hashing algorithms** - Comparing code efficiently
3. **Cross-file analysis** - Working with project-scale data
4. **Architecture patterns** - Suggesting consolidation

## Example Test Files

- `test_files/test_duplicates_a.py` - Functions with duplicates
- `test_files/test_duplicates_b.py` - Companion with matching duplicates

```bash
# Test duplicate detection
auto-refactor-ai test_files/test_duplicates_a.py test_files/test_duplicates_b.py --project
```

---

**V8 Status:** ✅ COMPLETE
**Next:** V9 - Git Integration & Pre-commit Hooks
