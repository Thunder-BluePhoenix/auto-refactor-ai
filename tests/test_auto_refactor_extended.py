"""Extended auto_refactor tests for improving coverage."""

from auto_refactor_ai.auto_refactor import (
    RefactorResult,
    RefactorSummary,
    apply_refactoring,
    format_diff_preview,
    format_refactor_summary,
    generate_diff,
    rollback_file,
)


class TestGenerateDiffExtended:
    """Extended tests for generate_diff function."""

    def test_diff_with_additions(self):
        """Test diff showing added lines."""
        original = "def foo():\n    pass\n"
        refactored = "def foo():\n    x = 1\n    pass\n"

        diff = generate_diff(original, refactored, "test.py")

        assert "+    x = 1" in diff
        assert "test.py" in diff

    def test_diff_with_deletions(self):
        """Test diff showing deleted lines."""
        original = "def foo():\n    x = 1\n    pass\n"
        refactored = "def foo():\n    pass\n"

        diff = generate_diff(original, refactored, "test.py")

        assert "-    x = 1" in diff


class TestApplyRefactoringExtended:
    """Extended tests for apply_refactoring function."""

    def test_apply_preserves_other_content(self, tmp_path):
        """Test that applying refactoring preserves other file content."""
        test_file = tmp_path / "test.py"
        original_content = "# Header\n\ndef foo():\n    pass\n\n# Footer\n"
        test_file.write_text(original_content)

        # Apply change to foo function only
        result = apply_refactoring(
            str(test_file),
            "def foo():\n    pass\n",
            "def foo():\n    return 1\n",
            3,  # start line
            4,  # end line
        )

        # File should be modified
        new_content = test_file.read_text()
        assert "# Header" in new_content
        assert "# Footer" in new_content


class TestRollbackFileExtended:
    """Extended tests for rollback_file function."""

    def test_rollback_preserves_backup(self, tmp_path):
        """Test that backup file is not deleted after rollback."""
        test_file = tmp_path / "test.py"
        backup_file = tmp_path / "test.py.bak"

        test_file.write_text("modified content")
        backup_file.write_text("original content")

        rollback_file(str(test_file), str(backup_file))

        # Original should be restored
        assert test_file.read_text() == "original content"


class TestRefactorResultExtended:
    """Extended tests for RefactorResult dataclass."""

    def test_refactor_result_with_error(self):
        """Test RefactorResult with error."""
        result = RefactorResult(
            file_path="test.py",
            function_name="foo",
            original_code="def foo(): pass",
            refactored_code="",
            start_line=1,
            end_line=1,
            error="Something went wrong",
        )

        assert result.error == "Something went wrong"
        assert result.applied is False

    def test_refactor_result_applied(self):
        """Test RefactorResult when applied."""
        result = RefactorResult(
            file_path="test.py",
            function_name="foo",
            original_code="def foo(): pass",
            refactored_code="def foo(): return 1",
            start_line=1,
            end_line=1,
            applied=True,
            backup_path="/backup/test.py",
        )

        assert result.applied is True
        assert result.backup_path == "/backup/test.py"


class TestRefactorSummaryExtended:
    """Extended tests for RefactorSummary dataclass."""

    def test_empty_summary(self):
        """Test empty summary."""
        summary = RefactorSummary(dry_run=True)

        assert summary.total_count == 0
        assert summary.applied_count == 0
        assert summary.skipped_count == 0
        assert summary.error_count == 0
        assert summary.dry_run is True

    def test_summary_with_results(self):
        """Test summary with results."""
        result = RefactorResult(
            file_path="test.py",
            function_name="foo",
            original_code="def foo(): pass",
            refactored_code="def foo(): return 1",
            start_line=1,
            end_line=1,
            diff="...",
            applied=True,
            backup_path=None,
            error=None,
        )

        summary = RefactorSummary(results=[result], dry_run=False)

        assert summary.total_count == 1
        assert summary.applied_count == 1
        assert summary.skipped_count == 0
        assert summary.error_count == 0

    def test_summary_with_mixed_results(self):
        """Test summary with mixed results."""
        applied_result = RefactorResult(
            file_path="test1.py",
            function_name="foo",
            original_code="",
            refactored_code="",
            start_line=1,
            end_line=1,
            applied=True,
        )
        skipped_result = RefactorResult(
            file_path="test2.py",
            function_name="bar",
            original_code="",
            refactored_code="",
            start_line=1,
            end_line=1,
            skipped=True,
        )
        error_result = RefactorResult(
            file_path="test3.py",
            function_name="baz",
            original_code="",
            refactored_code="",
            start_line=1,
            end_line=1,
            error="Failed",
        )

        summary = RefactorSummary(
            results=[applied_result, skipped_result, error_result], dry_run=False
        )

        assert summary.total_count == 3
        assert summary.applied_count == 1
        assert summary.skipped_count == 1
        assert summary.error_count == 1


class TestFormatDiffPreviewExtended:
    """Extended tests for format_diff_preview function."""

    def test_format_error_result(self):
        """Test formatting a result with error."""
        result = RefactorResult(
            file_path="test.py",
            function_name="foo",
            original_code="",
            refactored_code="",
            start_line=1,
            end_line=10,
            diff="",
            applied=False,
            backup_path=None,
            error="Something went wrong",
        )

        output = format_diff_preview(result)
        assert "Something went wrong" in output

    def test_format_applied_result(self):
        """Test formatting an applied result."""
        result = RefactorResult(
            file_path="test.py",
            function_name="foo",
            original_code="",
            refactored_code="",
            start_line=1,
            end_line=10,
            diff="+added line",
            applied=True,
            backup_path="/backup/test.py",
        )

        output = format_diff_preview(result)
        assert "Applied" in output
        assert "backup" in output.lower()

    def test_format_skipped_result(self):
        """Test formatting a skipped result."""
        result = RefactorResult(
            file_path="test.py",
            function_name="foo",
            original_code="",
            refactored_code="",
            start_line=1,
            end_line=10,
            skipped=True,
        )

        output = format_diff_preview(result)
        assert "Skipped" in output


class TestFormatRefactorSummaryExtended:
    """Extended tests for format_refactor_summary function."""

    def test_format_dry_run(self):
        """Test formatting dry-run summary."""
        summary = RefactorSummary(results=[], dry_run=True)

        output = format_refactor_summary(summary)
        assert "DRY RUN" in output

    def test_format_with_backup_dir(self):
        """Test formatting with backup directory."""
        result = RefactorResult(
            file_path="test.py",
            function_name="foo",
            original_code="",
            refactored_code="",
            start_line=1,
            end_line=1,
            applied=True,
        )
        summary = RefactorSummary(results=[result], backup_dir="/backups", dry_run=False)

        output = format_refactor_summary(summary)
        assert "backups" in output.lower()

    def test_format_with_errors(self):
        """Test formatting summary with errors."""
        error_result = RefactorResult(
            file_path="test.py",
            function_name="foo",
            original_code="",
            refactored_code="",
            start_line=1,
            end_line=1,
            error="Failed",
        )
        summary = RefactorSummary(results=[error_result], dry_run=False)

        output = format_refactor_summary(summary)
        assert "Errors: 1" in output
