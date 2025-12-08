# V7 Implementation Guide: Auto-Refactor Mode

## Overview

V7 transforms Auto Refactor AI from advice → action. The tool can now automatically apply AI-suggested refactorings with comprehensive safety features including backup, rollback, and dry-run capabilities.

## Goals

1. Enable automatic application of AI refactorings
2. Generate unified diff patches for review
3. Create backups before modifications
4. Support interactive approval and dry-run modes
5. Provide rollback capability

## New Features

### 1. `--apply` Flag

Apply AI-suggested refactorings automatically:

```bash
# Apply refactorings (with backup by default)
auto-refactor-ai mycode.py --ai-suggestions --apply

# Dry-run (show what would change)
auto-refactor-ai mycode.py --ai-suggestions --apply --dry-run

# Interactive mode (approve each change)
auto-refactor-ai mycode.py --ai-suggestions --apply --interactive
```

### 2. Backup System

```bash
# Default: creates backups in .auto-refactor-backup/
auto-refactor-ai mycode.py --ai-suggestions --apply

# Custom backup directory
auto-refactor-ai mycode.py --ai-suggestions --apply --backup-dir ./my-backups

# Disable backups (dangerous!)
auto-refactor-ai mycode.py --ai-suggestions --apply --no-backup
```

### 3. Dry-Run Mode

Preview changes without modifying files:

```bash
$ auto-refactor-ai test.py --ai-suggestions --apply --dry-run

🔧 Auto-Refactor Mode (DRY RUN)
   2 suggestion(s) to process

================================================================================
📝 REFACTORING: very_long_function()
================================================================================
File: test.py:1-55
--------------------------------------------------------------------------------

📋 CHANGES (unified diff):
----------------------------------------
--- a/test.py
+++ b/test.py
-def very_long_function(data):
-    # 55 lines...
+def very_long_function(data):
+    return process(validate(data))
+
+def validate(data):
+    if not data:
+        raise ValueError()
+    return data

================================================================================
🔧 AUTO-REFACTOR SUMMARY (DRY RUN)
================================================================================
Total Refactorings: 2
Applied: 0
Skipped: 0
Errors: 0

📋 This was a dry run. No files were modified.
   Remove --dry-run to apply changes.
================================================================================
```

### 4. Interactive Mode

Review and approve each change:

```bash
$ auto-refactor-ai test.py --ai-suggestions --apply --interactive

🔧 Auto-Refactor Mode (INTERACTIVE)

[Shows diff preview]

Apply this refactoring? [y/n/q] (yes/no/quit): y

✅ Applied successfully
   Backup: .auto-refactor-backup/test_20251208_031500.py
```

## New CLI Flags (V7)

| Flag | Description |
|------|-------------|
| `--apply` | Apply AI-suggested refactorings to files |
| `--dry-run` | Show what would be applied without changes |
| `--interactive` | Ask for approval before each change |
| `--backup` | Create backups (default: True) |
| `--no-backup` | Disable backup creation |
| `--backup-dir` | Directory for backups (default: `.auto-refactor-backup`) |

## Architecture

### New Module: `auto_refactor.py`

```python
@dataclass
class RefactorResult:
    file_path: str
    function_name: str
    original_code: str
    refactored_code: str
    backup_path: Optional[str]
    diff: str
    applied: bool
    skipped: bool
    error: Optional[str]

@dataclass
class RefactorSummary:
    results: List[RefactorResult]
    backup_dir: Optional[str]
    dry_run: bool

# Core functions
def generate_diff(original, refactored, file_path) -> str
def create_backup(file_path, backup_dir) -> str
def apply_refactoring(file_path, original, refactored, start, end) -> Tuple[bool, str]
def rollback_file(file_path, backup_path) -> Tuple[bool, str]
def auto_refactor(summary, dry_run, interactive, backup_dir) -> RefactorSummary
```

## Testing

### New Test File: `test_auto_refactor.py`

18 tests covering:
- `TestGenerateDiff` - Unified diff generation
- `TestCreateBackup` - Backup file creation
- `TestApplyRefactoring` - File modification
- `TestRollbackFile` - Rollback from backup
- `TestRefactorResult` - Result dataclass
- `TestRefactorSummary` - Summary with counts
- `TestFormatDiffPreview` - Display formatting
- `TestAutoRefactor` - End-to-end refactoring

### Running Tests

```bash
# Run all tests (131 tests)
pytest tests/ -v --no-cov

# Run only V7 tests
pytest tests/test_auto_refactor.py -v
```

## What You Learn

1. **Working with diffs** - `difflib` unified diff format
2. **Safe file operations** - Backup/restore patterns
3. **Destructive action protection** - Confirmation prompts
4. **User interaction in CLI** - Interactive mode design

## Security Considerations

1. **Always use backups** - Default is backup enabled
2. **Review diffs** - Use `--dry-run` first
3. **Test changes** - Run tests after applying
4. **Version control** - Commit before refactoring

## Example Workflow

```bash
# 1. Analyze code for issues
auto-refactor-ai myproject/ --format json

# 2. Preview AI suggestions
auto-refactor-ai myproject/ --ai-suggestions

# 3. Dry-run to see diffs
auto-refactor-ai myproject/ --ai-suggestions --apply --dry-run

# 4. Apply interactively
auto-refactor-ai myproject/ --ai-suggestions --apply --interactive

# 5. Or apply all at once
auto-refactor-ai myproject/ --ai-suggestions --apply
```

## Next Steps: V8 Preview

V8 will add **Project-Level Analysis**:

```bash
auto-refactor-ai myproject/ --plan
```

Features planned:
- Detect duplicate logic across files
- Suggest shared helper modules
- Identify code smells at project level
- Architectural recommendations

---

**V7 Status:** ✅ COMPLETE
**Next:** V8 - Project-Level Analysis
