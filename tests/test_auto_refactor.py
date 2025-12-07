"""Tests for auto_refactor module (V7)."""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from auto_refactor_ai.auto_refactor import (
    generate_diff,
    create_backup,
    apply_refactoring,
    rollback_file,
    process_single_refactoring,
    auto_refactor,
    format_diff_preview,
    format_refactor_summary,
    RefactorResult,
    RefactorSummary,
)
from auto_refactor_ai.ai_suggestions import AIAnalysisResult, AIAnalysisSummary
from auto_refactor_ai.llm_providers import RefactoringSuggestion
from auto_refactor_ai.analyzer import Issue, Severity


class TestGenerateDiff:
    """Test generate_diff function."""

    def test_simple_diff(self):
        """Test generating a simple diff."""
        original = "def foo():\n    pass\n"
        refactored = "def foo():\n    return 42\n"
        
        diff = generate_diff(original, refactored, "test.py")
        
        assert "--- a/test.py" in diff
        assert "+++ b/test.py" in diff
        assert "-    pass" in diff
        assert "+    return 42" in diff

    def test_no_changes(self):
        """Test diff when there are no changes."""
        code = "def foo():\n    pass\n"
        
        diff = generate_diff(code, code, "test.py")
        
        # No diff should be generated for identical code
        assert diff == ""

    def test_multiline_diff(self):
        """Test diff with multiple changes."""
        original = "def foo():\n    a = 1\n    b = 2\n    return a + b\n"
        refactored = "def foo():\n    return 1 + 2\n"
        
        diff = generate_diff(original, refactored, "file.py")
        
        assert "--- a/file.py" in diff
        assert "+++ b/file.py" in diff


class TestCreateBackup:
    """Test create_backup function."""

    def test_backup_creates_file(self):
        """Test that backup creates a copy of the file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source file
            source = Path(tmpdir) / "source.py"
            source.write_text("original content")
            
            # Create backup
            backup_dir = Path(tmpdir) / "backups"
            backup_path = create_backup(str(source), str(backup_dir))
            
            # Verify backup exists and has correct content
            assert os.path.exists(backup_path)
            with open(backup_path) as f:
                assert f.read() == "original content"

    def test_backup_creates_directory(self):
        """Test that backup creates the backup directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source.py"
            source.write_text("content")
            
            backup_dir = Path(tmpdir) / "new_backup_dir"
            assert not backup_dir.exists()
            
            create_backup(str(source), str(backup_dir))
            
            assert backup_dir.exists()


class TestApplyRefactoring:
    """Test apply_refactoring function."""

    def test_apply_simple_change(self):
        """Test applying a simple refactoring."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source file
            source = Path(tmpdir) / "test.py"
            original = "def foo():\n    pass\n"
            source.write_text(original)
            
            refactored = "def foo():\n    return 42\n"
            
            success, error = apply_refactoring(
                str(source),
                original,
                refactored,
                start_line=1,
                end_line=2,
            )
            
            assert success
            assert error is None
            assert source.read_text() == refactored

    def test_apply_to_middle_of_file(self):
        """Test applying refactoring in the middle of a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "test.py"
            original_content = "# Header\n\ndef foo():\n    pass\n\n# Footer\n"
            source.write_text(original_content)
            
            refactored = "def foo():\n    return 42\n"
            
            success, error = apply_refactoring(
                str(source),
                "def foo():\n    pass\n",
                refactored,
                start_line=3,
                end_line=4,
            )
            
            assert success
            content = source.read_text()
            assert "return 42" in content
            assert "# Header" in content
            assert "# Footer" in content


class TestRollbackFile:
    """Test rollback_file function."""

    def test_rollback_restores_original(self):
        """Test that rollback restores the original content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create original and modified files
            original = Path(tmpdir) / "original.py"
            modified = Path(tmpdir) / "modified.py"
            backup = Path(tmpdir) / "backup.py"
            
            original.write_text("original content")
            modified.write_text("modified content")
            backup.write_text("original content")
            
            success, error = rollback_file(str(modified), str(backup))
            
            assert success
            assert modified.read_text() == "original content"

    def test_rollback_missing_backup(self):
        """Test rollback with missing backup file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "target.py"
            target.write_text("content")
            
            success, error = rollback_file(str(target), "/nonexistent/backup.py")
            
            assert not success
            assert "not found" in error.lower()


class TestRefactorResult:
    """Test RefactorResult dataclass."""

    def test_result_creation(self):
        """Test creating a refactor result."""
        result = RefactorResult(
            file_path="test.py",
            function_name="foo",
            original_code="def foo(): pass",
            refactored_code="def foo(): return 42",
            start_line=1,
            end_line=1,
            applied=True,
        )
        
        assert result.file_path == "test.py"
        assert result.function_name == "foo"
        assert result.applied


class TestRefactorSummary:
    """Test RefactorSummary dataclass."""

    def test_summary_counts(self):
        """Test summary count properties."""
        results = [
            RefactorResult("a.py", "f1", "", "", 1, 1, applied=True),
            RefactorResult("b.py", "f2", "", "", 1, 1, applied=True),
            RefactorResult("c.py", "f3", "", "", 1, 1, skipped=True),
            RefactorResult("d.py", "f4", "", "", 1, 1, error="failed"),
        ]
        
        summary = RefactorSummary(results=results)
        
        assert summary.total_count == 4
        assert summary.applied_count == 2
        assert summary.skipped_count == 1
        assert summary.error_count == 1


class TestFormatDiffPreview:
    """Test format_diff_preview function."""

    def test_format_applied_result(self):
        """Test formatting an applied result."""
        result = RefactorResult(
            file_path="test.py",
            function_name="foo",
            original_code="def foo(): pass",
            refactored_code="def foo(): return 42",
            start_line=1,
            end_line=1,
            diff="--- a/test.py\n+++ b/test.py\n- pass\n+ return 42",
            applied=True,
            backup_path="/backup/test.py",
        )
        
        output = format_diff_preview(result)
        
        assert "REFACTORING" in output
        assert "foo()" in output
        assert "Applied successfully" in output
        assert "Backup:" in output

    def test_format_skipped_result(self):
        """Test formatting a skipped result."""
        result = RefactorResult(
            file_path="test.py",
            function_name="bar",
            original_code="",
            refactored_code="",
            start_line=1,
            end_line=1,
            skipped=True,
        )
        
        output = format_diff_preview(result)
        
        assert "Skipped" in output


class TestFormatRefactorSummary:
    """Test format_refactor_summary function."""

    def test_format_dry_run_summary(self):
        """Test formatting a dry run summary."""
        summary = RefactorSummary(
            results=[
                RefactorResult("a.py", "f1", "", "", 1, 1),
                RefactorResult("b.py", "f2", "", "", 1, 1),
            ],
            dry_run=True,
        )
        
        output = format_refactor_summary(summary)
        
        assert "DRY RUN" in output
        assert "No files were modified" in output

    def test_format_summary_with_backups(self):
        """Test formatting summary with backup info."""
        summary = RefactorSummary(
            results=[
                RefactorResult("a.py", "f1", "", "", 1, 1, applied=True),
            ],
            backup_dir=".backup",
        )
        
        output = format_refactor_summary(summary)
        
        assert "Backups saved to" in output


class TestProcessSingleRefactoring:
    """Test process_single_refactoring function."""

    def test_process_dry_run(self):
        """Test processing in dry run mode."""
        issue = Issue(
            severity=Severity.WARN,
            file="test.py",
            function_name="test_func",
            start_line=1,
            end_line=2,
            rule_name="test-rule",
            message="Test message",
        )
        
        suggestion = RefactoringSuggestion(
            original_code="def test_func(): pass",
            refactored_code="def test_func(): return 42",
            explanation="Added return",
            confidence=0.9,
        )
        
        ai_result = AIAnalysisResult(
            issue=issue,
            suggestion=suggestion,
            original_function_code="def test_func(): pass",
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create the source file
            source = Path(tmpdir) / "test.py"
            source.write_text("def test_func(): pass\n")
            ai_result.issue.file = str(source)
            
            result = process_single_refactoring(ai_result, dry_run=True)
            
            assert not result.applied
            assert result.diff  # Should have generated diff
            assert source.read_text() == "def test_func(): pass\n"  # Not modified


class TestAutoRefactor:
    """Test auto_refactor function."""

    def test_auto_refactor_dry_run(self):
        """Test auto refactor in dry run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "test.py"
            source.write_text("def foo():\n    pass\n")
            
            issue = Issue(
                severity=Severity.WARN,
                file=str(source),
                function_name="foo",
                start_line=1,
                end_line=2,
                rule_name="test",
                message="test",
            )
            
            suggestion = RefactoringSuggestion(
                original_code="def foo():\n    pass\n",
                refactored_code="def foo():\n    return 42\n",
                explanation="Added return",
                confidence=0.9,
            )
            
            ai_result = AIAnalysisResult(
                issue=issue,
                suggestion=suggestion,
                original_function_code="def foo():\n    pass\n",
            )
            
            ai_summary = AIAnalysisSummary(results=[ai_result])
            
            summary = auto_refactor(ai_summary, dry_run=True)
            
            assert summary.dry_run
            assert summary.total_count == 1
            assert source.read_text() == "def foo():\n    pass\n"  # Not modified

    def test_auto_refactor_empty_summary(self):
        """Test auto refactor with empty summary."""
        ai_summary = AIAnalysisSummary()
        
        summary = auto_refactor(ai_summary, dry_run=True)
        
        assert summary.total_count == 0
