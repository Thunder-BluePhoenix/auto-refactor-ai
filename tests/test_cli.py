"""Tests for CLI module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from auto_refactor_ai.analyzer import Issue, Severity
from auto_refactor_ai.cli import main, print_issues, print_json, print_summary
from auto_refactor_ai.config import Config


class TestPrintIssues:
    """Test print_issues function."""

    def test_print_no_issues(self, capsys):
        """Test printing when there are no issues."""
        print_issues([])
        captured = capsys.readouterr()
        assert "No issues found" in captured.out
        assert "✓" in captured.out

    def test_print_single_issue(self, capsys):
        """Test printing a single issue."""
        issue = Issue(
            severity=Severity.INFO,
            file="test.py",
            function_name="test_func",
            start_line=1,
            end_line=10,
            rule_name="test-rule",
            message="Test message",
        )
        print_issues([issue])
        captured = capsys.readouterr()
        assert "[INFO]" in captured.out
        assert "test.py:1-10" in captured.out
        assert "test_func()" in captured.out
        assert "Test message" in captured.out

    def test_print_multiple_issues_sorted_by_severity(self, capsys):
        """Test that issues are sorted by severity."""
        issues = [
            Issue(
                Severity.INFO,
                "file1.py",
                "func1",
                1,
                10,
                "rule1",
                "Info message",
            ),
            Issue(
                Severity.CRITICAL,
                "file2.py",
                "func2",
                1,
                10,
                "rule2",
                "Critical message",
            ),
            Issue(
                Severity.WARN,
                "file3.py",
                "func3",
                1,
                10,
                "rule3",
                "Warn message",
            ),
        ]
        print_issues(issues)
        captured = capsys.readouterr()

        # Check order: CRITICAL should come first
        critical_pos = captured.out.find("[CRITICAL]")
        warn_pos = captured.out.find("[WARN]")
        info_pos = captured.out.find("[INFO]")
        assert critical_pos < warn_pos < info_pos


class TestPrintSummary:
    """Test print_summary function."""

    def test_print_summary_no_issues(self, capsys):
        """Test printing summary with no issues."""
        print_summary([])
        captured = capsys.readouterr()
        # Should not print anything for no issues
        assert captured.out == ""

    def test_print_summary_with_issues(self, capsys):
        """Test printing summary with issues."""
        issues = [
            Issue(Severity.CRITICAL, "f.py", "f1", 1, 10, "r1", "m1"),
            Issue(Severity.CRITICAL, "f.py", "f2", 1, 10, "r2", "m2"),
            Issue(Severity.WARN, "f.py", "f3", 1, 10, "r3", "m3"),
            Issue(Severity.WARN, "f.py", "f4", 1, 10, "r4", "m4"),
            Issue(Severity.WARN, "f.py", "f5", 1, 10, "r5", "m5"),
            Issue(Severity.INFO, "f.py", "f6", 1, 10, "r6", "m6"),
        ]
        print_summary(issues)
        captured = capsys.readouterr()

        assert "SUMMARY" in captured.out
        assert "CRITICAL: 2" in captured.out
        assert "WARN:     3" in captured.out
        assert "INFO:     1" in captured.out
        assert "TOTAL:    6" in captured.out


class TestPrintJson:
    """Test print_json function."""

    def test_print_json_no_issues(self, capsys):
        """Test JSON output with no issues."""
        config = Config()
        print_json([], config)
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert data["summary"]["total"] == 0
        assert data["summary"]["critical"] == 0
        assert data["summary"]["warn"] == 0
        assert data["summary"]["info"] == 0
        assert data["issues"] == []
        assert "config" in data

    def test_print_json_with_issues(self, capsys):
        """Test JSON output with issues."""
        config = Config(max_function_length=25)
        issues = [
            Issue(Severity.CRITICAL, "test.py", "func1", 1, 50, "rule1", "message1"),
            Issue(Severity.INFO, "test.py", "func2", 60, 70, "rule2", "message2"),
        ]
        print_json(issues, config)
        captured = capsys.readouterr()

        data = json.loads(captured.out)
        assert data["summary"]["total"] == 2
        assert data["summary"]["critical"] == 1
        assert data["summary"]["info"] == 1
        assert len(data["issues"]) == 2
        assert data["config"]["max_function_length"] == 25


class TestMainCLI:
    """Test main CLI function."""

    def test_main_with_help(self):
        """Test running with --help flag."""
        with patch("sys.argv", ["auto-refactor-ai", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_with_nonexistent_path(self, capsys):
        """Test running with non-existent path."""
        with patch("sys.argv", ["auto-refactor-ai", "nonexistent_file.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "ERROR" in captured.out

    def test_main_with_good_file(self, capsys):
        """Test analyzing a good Python file."""
        code = """
def simple_function(x):
    return x + 1
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            with patch("sys.argv", ["auto-refactor-ai", temp_path]):
                main()
                captured = capsys.readouterr()
                assert "No issues found" in captured.out or "✓" in captured.out
        finally:
            Path(temp_path).unlink()

    def test_main_with_json_format(self, capsys):
        """Test running with JSON output format."""
        code = """
def simple_function(x):
    return x + 1
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            with patch("sys.argv", ["auto-refactor-ai", temp_path, "--format", "json"]):
                main()
                captured = capsys.readouterr()
                # Should be valid JSON
                data = json.loads(captured.out)
                assert "config" in data
                assert "summary" in data
                assert "issues" in data
        finally:
            Path(temp_path).unlink()

    def test_main_with_custom_thresholds(self, capsys):
        """Test running with custom thresholds."""
        code = """
def func(a, b, c, d, e, f):
    return a + b + c + d + e + f
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            with patch(
                "sys.argv",
                [
                    "auto-refactor-ai",
                    temp_path,
                    "--max-params",
                    "3",
                    "--format",
                    "json",
                ],
            ):
                main()
                captured = capsys.readouterr()
                data = json.loads(captured.out)
                # Should find parameter issue
                assert data["summary"]["total"] > 0
        finally:
            Path(temp_path).unlink()

    def test_main_with_directory(self, capsys):
        """Test analyzing a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file in the directory
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def simple(): pass")

            with patch("sys.argv", ["auto-refactor-ai", tmpdir]):
                main()
                captured = capsys.readouterr()
                # Should run without error
                assert "SUMMARY" in captured.out or "No issues" in captured.out

    def test_main_with_config_file(self, capsys):
        """Test running with config file."""
        # Create config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as config_f:
            config_f.write(
                """
max_function_length = 10
max_parameters = 2
max_nesting_depth = 1
"""
            )
            config_f.flush()
            config_path = config_f.name

        # Create test file
        code = "def func(): pass"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            test_path = f.name

        try:
            with patch(
                "sys.argv",
                ["auto-refactor-ai", test_path, "--config", config_path, "--format", "json"],
            ):
                main()
                captured = capsys.readouterr()
                data = json.loads(captured.out)
                # Config should be loaded
                assert data["config"]["max_function_length"] == 10
                assert data["config"]["max_parameters"] == 2
        finally:
            Path(test_path).unlink()
            Path(config_path).unlink()

    def test_cli_override_config(self, capsys):
        """Test that CLI arguments override config file."""
        # Create config file with one value
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as config_f:
            config_f.write("max_function_length = 100\n")
            config_f.flush()
            config_path = config_f.name

        # Create test file
        code = "def func(): pass"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            test_path = f.name

        try:
            with patch(
                "sys.argv",
                [
                    "auto-refactor-ai",
                    test_path,
                    "--config",
                    config_path,
                    "--max-len",
                    "5",  # Override
                    "--format",
                    "json",
                ],
            ):
                main()
                captured = capsys.readouterr()
                data = json.loads(captured.out)
                # CLI should override config
                assert data["config"]["max_function_length"] == 5
        finally:
            Path(test_path).unlink()
            Path(config_path).unlink()
