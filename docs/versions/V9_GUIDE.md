# V9 Implementation Guide: Git Integration

## Overview

V9 integrates with Git to enable efficient analysis of only changed files, making the tool practical for daily development workflows.

## Goals

1.  Run analysis only on modified files
2.  Support staged files for pre-commit workflows
3.  Provide configuration for pre-commit framework

## New CLI Flags (V9)

| Flag | Description |
|------|-------------|
| `--git` | Analyze modified files in git working tree |
| `--staged` | Analyze files staged for commit |

## Usage

```bash
# Analyze all modified (unstaged) Python files
auto-refactor-ai . --git

# Analyze only staged files (for pre-commit)
auto-refactor-ai . --staged

# Combine with other flags
auto-refactor-ai . --git --format json
auto-refactor-ai . --staged --explain
```

## Architecture

### New Module: `git_utils.py`

```python
def is_git_repo(path: str) -> bool:
    """Check if path is inside a git repository."""

def get_changed_files(path: str, staged: bool = False) -> List[str]:
    """Get list of changed Python files."""
```

### Pre-commit Configuration

File: `.pre-commit-hooks.yaml`

```yaml
- id: auto-refactor-ai
  name: Auto Refactor AI
  entry: auto-refactor-ai
  language: python
  types: [python]
```

Usage in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/your-org/auto-refactor-ai
    rev: v0.9.0
    hooks:
      - id: auto-refactor-ai
```

## Testing

```bash
# Run V9 tests
pytest tests/test_git_utils.py -v

# All tests (157 total)
pytest tests/ -v --no-cov
```

---

**V9 Status:** ✅ COMPLETE
**Next:** V10 - Refactor Planning Mode
