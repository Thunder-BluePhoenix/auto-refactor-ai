# Test Files

This directory contains test files to validate the auto-refactor-ai analyzer.

## Test Files Overview

### `test_perfect_code.py`
- **Purpose**: Demonstrates well-written code with NO issues
- **Expected Result**: No warnings or errors
- **What it tests**: Validates that good code passes all checks

### `test_length_issues.py`
- **Purpose**: Tests Rule 1 (Function Length)
- **Contains**:
  - Functions at various lengths (3, 20, 30, 35, 50, 70 lines)
  - Tests INFO, WARN, and CRITICAL severity levels
- **Expected Results**:
  - 30 lines or less: ✅ No issues
  - 31-45 lines: ℹ️ INFO
  - 46-60 lines: ⚠️ WARN
  - 60+ lines: 🔴 CRITICAL

### `test_parameter_issues.py`
- **Purpose**: Tests Rule 2 (Too Many Parameters)
- **Contains**:
  - Functions with 2, 5, 6, 8, 12 parameters
  - Tests with *args, **kwargs, keyword-only args
  - Examples of good refactoring (config objects)
- **Expected Results**:
  - ≤5 params: ✅ No issues
  - 6-7 params: ℹ️ INFO
  - 8-10 params: ⚠️ WARN
  - 10+ params: 🔴 CRITICAL

### `test_nesting_issues.py`
- **Purpose**: Tests Rule 3 (Deep Nesting)
- **Contains**:
  - Functions with 0-7 levels of nesting
  - Mixed control structures (if/for/while/with)
  - Examples of good patterns (early returns, helper functions)
- **Expected Results**:
  - ≤3 levels: ✅ No issues
  - 4 levels: ℹ️ INFO
  - 5-6 levels: ⚠️ WARN
  - 7+ levels: 🔴 CRITICAL

### `test_combined_issues.py`
- **Purpose**: Tests functions that violate multiple rules
- **Contains**:
  - Functions with 2-3 simultaneous violations
  - Varying severity combinations
  - "Nightmare" functions that violate all rules
- **Expected Results**: Multiple issues per function

### `test_edge_cases.py`
- **Purpose**: Tests special cases and edge scenarios
- **Contains**:
  - Empty functions
  - One-liners
  - Nested functions
  - Async functions
  - Generators
  - Class methods (instance, class, static)
  - Decorators
  - Exception handling
  - Unicode function names
- **Expected Results**: Varies by case

### `sample_test.py` (Original V0 test file)
- **Purpose**: Original test file from V0
- **Contains**: Long functions with comments
- **Status**: Legacy test file, kept for compatibility

### `test_sample.py`
- **Purpose**: Comprehensive test from V1 development
- **Contains**: Examples of all three rules
- **Status**: Used during V1 development

## Running Tests

### Test a specific file
```bash
python -m auto_refactor_ai test_files/test_perfect_code.py
```

### Test all files in directory
```bash
python -m auto_refactor_ai test_files/
```

### Test with custom thresholds
```bash
python -m auto_refactor_ai test_files/ --max-len 20 --max-params 3 --max-nesting 2
```

## Expected Total Issues (default thresholds)

When running on the entire `test_files/` directory with default settings:

- **test_perfect_code.py**: 0 issues ✅
- **test_length_issues.py**: ~3 issues
- **test_parameter_issues.py**: ~5 issues
- **test_nesting_issues.py**: ~4 issues
- **test_combined_issues.py**: ~10+ issues
- **test_edge_cases.py**: ~2 issues

**Total**: ~24-30 issues expected

## Adding New Test Files

When adding new test files:

1. Name them with `test_` prefix
2. Add clear docstrings explaining what they test
3. Include comments showing expected severity levels
4. Update this README with the new file description
5. Test with: `python -m auto_refactor_ai test_files/your_new_file.py`

## Severity Level Quick Reference

| Severity | Function Length | Parameters | Nesting Depth |
|----------|----------------|------------|---------------|
| ✅ OK     | ≤ 30 lines     | ≤ 5        | ≤ 3 levels    |
| ℹ️ INFO   | 31-45 lines    | 6-7        | 4 levels      |
| ⚠️ WARN   | 46-60 lines    | 8-10       | 5-6 levels    |
| 🔴 CRITICAL| 60+ lines     | 10+        | 7+ levels     |

*Note: Exact thresholds are 1x (OK), 1.5x (INFO/WARN boundary), 2x (WARN/CRITICAL boundary)*
