"""Auto-refactor module for applying AI suggestions (V7).

This module provides functionality to automatically apply AI-generated
refactoring suggestions, with backup, rollback, and dry-run capabilities.
"""

import difflib
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from .ai_suggestions import AIAnalysisResult, AIAnalysisSummary


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


@dataclass
class RefactorSummary:
    """Summary of all refactoring operations."""

    results: List[RefactorResult] = field(default_factory=list)
    backup_dir: Optional[str] = None
    dry_run: bool = False

    @property
    def total_count(self) -> int:
        return len(self.results)

    @property
    def applied_count(self) -> int:
        return sum(1 for r in self.results if r.applied)

    @property
    def skipped_count(self) -> int:
        return sum(1 for r in self.results if r.skipped)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.error)


def generate_diff(
    original: str, refactored: str, file_path: str = "file.py", context_lines: int = 3
) -> str:
    """Generate a unified diff between original and refactored code.

    Args:
        original: Original source code
        refactored: Refactored source code
        file_path: File path for diff header
        context_lines: Number of context lines in diff

    Returns:
        Unified diff string
    """
    original_lines = original.splitlines(keepends=True)
    refactored_lines = refactored.splitlines(keepends=True)

    # Ensure lines end with newline for proper diff
    if original_lines and not original_lines[-1].endswith("\n"):
        original_lines[-1] += "\n"
    if refactored_lines and not refactored_lines[-1].endswith("\n"):
        refactored_lines[-1] += "\n"

    diff = difflib.unified_diff(
        original_lines,
        refactored_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        n=context_lines,
    )

    return "".join(diff)


def create_backup(file_path: str, backup_dir: str) -> str:
    """Create a backup of a file before modification.

    Args:
        file_path: Path to the file to backup
        backup_dir: Directory to store backups

    Returns:
        Path to the backup file
    """
    # Create backup directory if it doesn't exist
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)

    # Create timestamp-based backup filename
    source_path = Path(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"

    # Preserve directory structure in backup
    relative_dir = source_path.parent.name if source_path.parent.name else ""
    if relative_dir:
        (backup_path / relative_dir).mkdir(parents=True, exist_ok=True)
        backup_file = backup_path / relative_dir / backup_name
    else:
        backup_file = backup_path / backup_name

    # Copy the file
    shutil.copy2(file_path, backup_file)

    return str(backup_file)


def apply_refactoring(
    file_path: str, original_function: str, refactored_code: str, start_line: int, end_line: int
) -> Tuple[bool, Optional[str]]:
    """Apply refactored code to a file.

    This replaces the original function code with the refactored version.

    Args:
        file_path: Path to the file to modify
        original_function: Original function code to replace
        refactored_code: New code to insert
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)

    Returns:
        Tuple of (success, error_message)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Convert to 0-indexed
        start_idx = start_line - 1
        end_idx = end_line

        # Get the indentation of the original function
        original_indent = ""
        if lines[start_idx]:
            original_indent = lines[start_idx][
                : len(lines[start_idx]) - len(lines[start_idx].lstrip())
            ]

        # Prepare refactored code with proper indentation
        refactored_lines = refactored_code.splitlines(keepends=True)

        # Ensure last line has newline
        if refactored_lines and not refactored_lines[-1].endswith("\n"):
            refactored_lines[-1] += "\n"

        # Replace lines
        new_lines = lines[:start_idx] + refactored_lines + lines[end_idx:]

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        return True, None

    except Exception as e:
        return False, str(e)


def rollback_file(file_path: str, backup_path: str) -> Tuple[bool, Optional[str]]:
    """Rollback a file to its backup version.

    Args:
        file_path: Path to the file to rollback
        backup_path: Path to the backup file

    Returns:
        Tuple of (success, error_message)
    """
    try:
        if not os.path.exists(backup_path):
            return False, f"Backup file not found: {backup_path}"

        shutil.copy2(backup_path, file_path)
        return True, None

    except Exception as e:
        return False, str(e)


def format_diff_preview(result: RefactorResult) -> str:
    """Format a refactoring result for preview display.

    Args:
        result: The refactoring result to format

    Returns:
        Formatted string for display
    """
    lines = []

    lines.append("\n" + "=" * 80)
    lines.append(f"📝 REFACTORING: {result.function_name}()")
    lines.append("=" * 80)
    lines.append(f"File: {result.file_path}:{result.start_line}-{result.end_line}")
    lines.append("-" * 80)

    if result.diff:
        lines.append("\n📋 CHANGES (unified diff):")
        lines.append("-" * 40)
        # Color-code the diff for terminal
        for line in result.diff.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                lines.append(f"  {line}")  # Added lines
            elif line.startswith("-") and not line.startswith("---"):
                lines.append(f"  {line}")  # Removed lines
            else:
                lines.append(f"  {line}")

    if result.applied:
        lines.append(f"\n✅ Applied successfully")
        if result.backup_path:
            lines.append(f"   Backup: {result.backup_path}")
    elif result.skipped:
        lines.append(f"\n⏭️  Skipped by user")
    elif result.error:
        lines.append(f"\n❌ Error: {result.error}")

    return "\n".join(lines)


def format_refactor_summary(summary: RefactorSummary) -> str:
    """Format the refactoring summary for display.

    Args:
        summary: The refactoring summary

    Returns:
        Formatted string for display
    """
    lines = []

    lines.append("\n" + "=" * 80)
    lines.append("🔧 AUTO-REFACTOR SUMMARY" + (" (DRY RUN)" if summary.dry_run else ""))
    lines.append("=" * 80)
    lines.append(f"Total Refactorings: {summary.total_count}")
    lines.append(f"Applied: {summary.applied_count}")
    lines.append(f"Skipped: {summary.skipped_count}")
    lines.append(f"Errors: {summary.error_count}")

    if summary.backup_dir and summary.applied_count > 0:
        lines.append(f"\n💾 Backups saved to: {summary.backup_dir}")
        lines.append("   To rollback: auto-refactor-ai --rollback <backup-file>")

    if summary.dry_run:
        lines.append("\n📋 This was a dry run. No files were modified.")
        lines.append("   Remove --dry-run to apply changes.")

    lines.append("=" * 80 + "\n")

    return "\n".join(lines)


def process_single_refactoring(
    ai_result: AIAnalysisResult,
    dry_run: bool = True,
    backup_dir: Optional[str] = None,
) -> RefactorResult:
    """Process a single AI suggestion and optionally apply it.

    Args:
        ai_result: The AI analysis result with suggestion
        dry_run: If True, don't actually modify files
        backup_dir: Directory for backups (required if not dry_run)

    Returns:
        RefactorResult with outcome
    """
    result = RefactorResult(
        file_path=ai_result.issue.file,
        function_name=ai_result.issue.function_name,
        original_code=ai_result.original_function_code,
        refactored_code=ai_result.suggestion.refactored_code,
        start_line=ai_result.issue.start_line,
        end_line=ai_result.issue.end_line,
    )

    # Check if we have valid refactored code
    if not ai_result.suggestion.refactored_code:
        result.error = "No refactored code provided"
        return result

    # Generate diff
    result.diff = generate_diff(
        ai_result.original_function_code,
        ai_result.suggestion.refactored_code,
        ai_result.issue.file,
    )

    if dry_run:
        result.applied = False
        return result

    # Create backup before applying
    if backup_dir:
        try:
            result.backup_path = create_backup(ai_result.issue.file, backup_dir)
        except Exception as e:
            result.error = f"Failed to create backup: {e}"
            return result

    # Apply the refactoring
    success, error = apply_refactoring(
        ai_result.issue.file,
        ai_result.original_function_code,
        ai_result.suggestion.refactored_code,
        ai_result.issue.start_line,
        ai_result.issue.end_line,
    )

    if success:
        result.applied = True
    else:
        result.error = error
        # Try to rollback if we have a backup
        if result.backup_path:
            rollback_file(ai_result.issue.file, result.backup_path)

    return result


def prompt_for_approval(result: RefactorResult) -> bool:
    """Prompt user for approval to apply a refactoring.

    Args:
        result: The refactoring result to approve

    Returns:
        True if approved, False otherwise
    """
    print(format_diff_preview(result))
    print("\n" + "-" * 40)

    while True:
        response = input("Apply this refactoring? [y/n/q] (yes/no/quit): ").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        elif response in ("q", "quit"):
            raise KeyboardInterrupt("User quit")
        else:
            print("Please enter 'y' (yes), 'n' (no), or 'q' (quit)")


def auto_refactor(
    ai_summary: AIAnalysisSummary,
    dry_run: bool = True,
    interactive: bool = False,
    backup_dir: str = ".auto-refactor-backup",
    create_backups: bool = True,
) -> RefactorSummary:
    """Apply AI suggestions to refactor code.

    Args:
        ai_summary: Summary from AI analysis with suggestions
        dry_run: If True, show what would be done without applying
        interactive: If True, prompt for approval before each change
        backup_dir: Directory to store backups
        create_backups: If True, create backups before modifying

    Returns:
        Summary of all refactoring operations
    """
    summary = RefactorSummary(
        backup_dir=backup_dir if create_backups and not dry_run else None,
        dry_run=dry_run,
    )

    if not ai_summary.results:
        return summary

    for ai_result in ai_summary.results:
        # Skip if no valid refactored code
        if not ai_result.suggestion.refactored_code:
            result = RefactorResult(
                file_path=ai_result.issue.file,
                function_name=ai_result.issue.function_name,
                original_code=ai_result.original_function_code,
                refactored_code="",
                start_line=ai_result.issue.start_line,
                end_line=ai_result.issue.end_line,
                error="No refactored code available",
            )
            summary.results.append(result)
            continue

        # Process the refactoring (dry-run first to generate diff)
        result = process_single_refactoring(
            ai_result,
            dry_run=True,  # Always generate diff first
            backup_dir=backup_dir if create_backups else None,
        )

        if dry_run:
            # Just show the diff
            print(format_diff_preview(result))
            summary.results.append(result)
            continue

        # Interactive mode - ask for approval
        if interactive:
            try:
                approved = prompt_for_approval(result)
                if not approved:
                    result.skipped = True
                    summary.results.append(result)
                    continue
            except KeyboardInterrupt:
                print("\n\n⚠️  Refactoring cancelled by user")
                break

        # Actually apply the refactoring
        result = process_single_refactoring(
            ai_result,
            dry_run=False,
            backup_dir=backup_dir if create_backups else None,
        )

        if not interactive:
            print(format_diff_preview(result))

        summary.results.append(result)

    return summary


def print_refactor_results(summary: RefactorSummary) -> None:
    """Print refactoring results to stdout.

    Args:
        summary: The refactoring summary
    """
    print(format_refactor_summary(summary))
