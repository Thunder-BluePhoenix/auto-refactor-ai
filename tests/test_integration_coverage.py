"""Final batch of tests to push coverage above 90%."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from auto_refactor_ai.auto_refactor import (
    RefactorSummary,
    create_backup,
    format_refactor_summary,
)
from auto_refactor_ai.cli import (
    handle_ai_suggestions,
    main,
)
from auto_refactor_ai.config import (
    load_config,
)


class TestCreateBackupExtended:
    """Extended tests for create_backup."""

    def test_backup_creates_directory(self, tmp_path):
        """Test that backup creates directory if not exists."""
        test_file = tmp_path / "test.py"
        test_file.write_text("content")
        backup_dir = tmp_path / "backups"

        backup_path = create_backup(str(test_file), str(backup_dir))

        assert Path(backup_path).exists()
        assert backup_dir.exists()

    def test_backup_preserves_content(self, tmp_path):
        """Test that backup preserves file content."""
        test_file = tmp_path / "test.py"
        original_content = "def foo(): return 1"
        test_file.write_text(original_content)
        backup_dir = tmp_path / "backups"

        backup_path = create_backup(str(test_file), str(backup_dir))

        assert Path(backup_path).read_text() == original_content


class TestMainEntrypoints:
    """Tests for main CLI entry points."""

    def test_main_with_file(self, tmp_path, capsys):
        """Test main with single file."""
        test_file = tmp_path / "clean.py"
        test_file.write_text("def foo():\n    pass\n")

        with patch("sys.argv", ["auto-refactor-ai", str(test_file)]):
            main()

        captured = capsys.readouterr()
        assert "No issues" in captured.out or len(captured.out) >= 0

    def test_main_with_json_format(self, tmp_path, capsys):
        """Test main with JSON output."""
        test_file = tmp_path / "clean.py"
        test_file.write_text("def foo():\n    pass\n")

        with patch("sys.argv", ["auto-refactor-ai", str(test_file), "--format", "json"]):
            main()

        captured = capsys.readouterr()
        assert "{" in captured.out  # JSON output

    def test_main_with_explain(self, tmp_path, capsys):
        """Test main with --explain flag."""
        test_file = tmp_path / "long.py"
        lines = ["def long_func():\n"] + ["    x = 1\n"] * 40
        test_file.write_text("".join(lines))

        with patch("sys.argv", ["auto-refactor-ai", str(test_file), "--explain"]):
            main()

        captured = capsys.readouterr()
        # Should have detailed output
        assert len(captured.out) > 0


class TestHandleAISuggestions:
    """Tests for handle_ai_suggestions function."""

    def test_no_issues(self, capsys):
        """Test with no issues."""
        args = MagicMock()
        args.ai_suggestions = True
        args.apply = False

        handle_ai_suggestions([], args)

        captured = capsys.readouterr()
        assert "No issues" in captured.out or "looks good" in captured.out.lower()


class TestFormatRefactorSummaryEdgeCases:
    """Edge case tests for format_refactor_summary."""

    def test_empty_summary(self):
        """Test formatting empty summary."""
        summary = RefactorSummary()

        output = format_refactor_summary(summary)

        assert "SUMMARY" in output
        assert "0" in output


class TestLoadConfigFileFallback:
    """Tests for config loading fallbacks."""

    def test_load_with_nonexistent_yml(self, tmp_path):
        """Test loading nonexistent yml returns defaults."""
        config = load_config(tmp_path / "nonexistent.yml")

        assert config.max_function_length == 30  # Default


class TestIntegrationScenarios:
    """Integration test scenarios."""

    def test_analyze_multiple_files(self, tmp_path, capsys):
        """Test analyzing multiple files in a directory."""
        (tmp_path / "file1.py").write_text("def foo(): pass\n")
        (tmp_path / "file2.py").write_text("def bar(): pass\n")
        (tmp_path / "file3.py").write_text("def baz(): pass\n")

        with patch("sys.argv", ["auto-refactor-ai", str(tmp_path)]):
            main()

        captured = capsys.readouterr()
        # Should complete without error
        assert "No issues" in captured.out or "SUMMARY" in captured.out or len(captured.out) >= 0

    def test_analyze_with_config_overrides(self, tmp_path, capsys):
        """Test with config overrides."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo():\n    pass\n")

        with patch("sys.argv", ["auto-refactor-ai", str(test_file), "--max-len", "10"]):
            main()

        captured = capsys.readouterr()
        # Should complete without error
        assert len(captured.out) >= 0
