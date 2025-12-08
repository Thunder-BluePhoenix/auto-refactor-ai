"""Additional CLI tests for handlers and git integration."""

from unittest.mock import MagicMock, patch

import pytest

from auto_refactor_ai.cli import (
    handle_project_analysis,
    handle_refactor_plan,
)


class TestHandleProjectAnalysis:
    """Tests for handle_project_analysis function."""

    def test_project_analysis_with_valid_path(self, tmp_path, capsys):
        """Test project analysis with a valid path."""
        # Create test files
        (tmp_path / "test.py").write_text("def foo():\n    pass\n")

        args = MagicMock()
        args.path = str(tmp_path)
        args.similarity_threshold = 0.8
        args.min_lines = 5

        handle_project_analysis(args)

        captured = capsys.readouterr()
        assert "Analyzing project" in captured.out

    def test_project_analysis_nonexistent_path(self, capsys):
        """Test project analysis with nonexistent path."""
        args = MagicMock()
        args.path = "/nonexistent/path"
        args.similarity_threshold = 0.8
        args.min_lines = 5

        handle_project_analysis(args)

        captured = capsys.readouterr()
        assert "ERROR" in captured.out or "not found" in captured.out.lower()


class TestHandleRefactorPlan:
    """Tests for handle_refactor_plan function."""

    def test_refactor_plan_with_issues(self, tmp_path, capsys):
        """Test refactor plan generation."""
        # Create a test file with issues
        test_file = tmp_path / "long.py"
        lines = ["def long_func():\n"] + ["    x = 1\n"] * 50
        test_file.write_text("".join(lines))

        from auto_refactor_ai.analyzer import Issue, Severity

        issues = [
            Issue(
                file=str(test_file),
                function_name="long_func",
                start_line=1,
                end_line=51,
                severity=Severity.CRITICAL,
                message="Function too long",
                rule_name="function-too-long",
                details={"length": 51, "max_length": 30},
            )
        ]

        args = MagicMock()
        args.path = str(tmp_path)
        args.min_lines = 5
        args.similarity_threshold = 0.8
        args.ai_suggestions = False
        args.plan_format = "text"

        from auto_refactor_ai.config import Config

        config = Config()

        handle_refactor_plan(args, config, issues)

        captured = capsys.readouterr()
        assert "REFACTORING PLAN" in captured.out or "Analyzed" in captured.out


class TestGitIntegration:
    """Tests for git integration paths."""

    def test_collect_files_with_git_not_repo(self, tmp_path):
        """Test error when directory is not a git repo."""
        from auto_refactor_ai.cli import collect_files_to_analyze
        from auto_refactor_ai.config import Config

        args = MagicMock()
        args.path = str(tmp_path)
        args.git = True
        args.staged = False

        config = Config()

        with pytest.raises(SystemExit):
            collect_files_to_analyze(args, config)


class TestMainFunction:
    """Tests for main CLI function."""

    def test_main_with_check_providers(self):
        """Test --check-providers flag."""
        from auto_refactor_ai.cli import main

        with patch("sys.argv", ["auto-refactor-ai", "--check-providers"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_with_project_flag(self, tmp_path):
        """Test --project flag."""
        from auto_refactor_ai.cli import main

        (tmp_path / "test.py").write_text("def foo(): pass\n")

        with patch("sys.argv", ["auto-refactor-ai", str(tmp_path), "--project"]):
            main()  # Should run without error

    def test_main_with_plan_flag(self, tmp_path):
        """Test --plan flag."""
        from auto_refactor_ai.cli import main

        (tmp_path / "test.py").write_text("def foo(): pass\n")

        with patch("sys.argv", ["auto-refactor-ai", str(tmp_path), "--plan"]):
            main()  # Should run without error


class TestLLMProviderChecks:
    """Tests for LLM provider availability checks."""

    def test_get_provider_status_message(self):
        """Test getting provider status message."""
        from auto_refactor_ai.ai_suggestions import get_provider_status_message

        message = get_provider_status_message()

        # Should contain provider names
        assert (
            "openai" in message.lower() or "anthropic" in message.lower() or "Available" in message
        )


class TestExplanationsIntegration:
    """Tests for explanations in CLI output."""

    def test_print_issues_with_verbose_explanations(self, capsys):
        """Test verbose explanations output."""
        from auto_refactor_ai.analyzer import Issue, Severity
        from auto_refactor_ai.cli import print_issues_with_explanations

        issues = [
            Issue(
                file="test.py",
                function_name="foo",
                start_line=1,
                end_line=50,
                severity=Severity.CRITICAL,
                message="Function too long",
                rule_name="function-too-long",
                details={},
            )
        ]

        print_issues_with_explanations(issues, verbose=True, summary=False)

        captured = capsys.readouterr()
        # Should contain explanation content
        assert "CRITICAL" in captured.out or "function" in captured.out.lower()

    def test_print_issues_with_summary_explanations(self, capsys):
        """Test summary explanations output."""
        from auto_refactor_ai.analyzer import Issue, Severity
        from auto_refactor_ai.cli import print_issues_with_explanations

        issues = [
            Issue(
                file="test.py",
                function_name="bar",
                start_line=1,
                end_line=20,
                severity=Severity.WARN,
                message="Too many params",
                rule_name="too-many-parameters",
                details={},
            )
        ]

        print_issues_with_explanations(issues, verbose=False, summary=True)

        captured = capsys.readouterr()
        assert len(captured.out) > 0
