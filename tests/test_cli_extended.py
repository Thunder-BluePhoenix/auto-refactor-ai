"""Extended CLI tests for improving coverage."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from auto_refactor_ai.analyzer import Issue, Severity
from auto_refactor_ai.cli import (
    analyze_directory,
    analyze_single_file,
    apply_config_overrides,
    collect_files_to_analyze,
    create_argument_parser,
    output_results,
    print_issues_with_explanations,
    run_analysis,
)
from auto_refactor_ai.config import Config


@pytest.fixture
def sample_issues():
    """Create sample issues for testing."""
    return [
        Issue(
            file="test.py",
            function_name="test_func",
            start_line=1,
            end_line=50,
            severity=Severity.CRITICAL,
            message="Function too long",
            rule_name="function-too-long",
            details={"length": 50, "max_length": 30},
        ),
        Issue(
            file="test.py",
            function_name="another_func",
            start_line=60,
            end_line=80,
            severity=Severity.WARN,
            message="Too many parameters",
            rule_name="too-many-parameters",
            details={"params": 7, "max_params": 5},
        ),
    ]


class TestApplyConfigOverrides:
    """Tests for apply_config_overrides function."""

    def test_override_max_len(self):
        """Test overriding max_len from CLI."""
        config = Config()
        args = MagicMock()
        args.max_len = 20
        args.max_params = None
        args.max_nesting = None

        result = apply_config_overrides(config, args)
        assert result.max_function_length == 20

    def test_override_all_params(self):
        """Test overriding all parameters from CLI."""
        config = Config()
        args = MagicMock()
        args.max_len = 25
        args.max_params = 3
        args.max_nesting = 2

        result = apply_config_overrides(config, args)
        assert result.max_function_length == 25
        assert result.max_parameters == 3
        assert result.max_nesting_depth == 2

    def test_no_overrides(self):
        """Test no overrides keeps defaults."""
        config = Config()
        args = MagicMock()
        args.max_len = None
        args.max_params = None
        args.max_nesting = None

        result = apply_config_overrides(config, args)
        assert result.max_function_length == 30
        assert result.max_parameters == 5
        assert result.max_nesting_depth == 3


class TestCollectFilesToAnalyze:
    """Tests for collect_files_to_analyze function."""

    def test_collect_single_file(self, tmp_path):
        """Test collecting a single file."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass\n")

        args = MagicMock()
        args.path = str(test_file)
        args.git = False
        args.staged = False

        config = Config()
        files, target = collect_files_to_analyze(args, config)

        assert len(files) == 1
        assert str(test_file) in files[0]

    def test_collect_directory(self, tmp_path):
        """Test collecting from a directory."""
        # Create test files
        (tmp_path / "file1.py").write_text("def foo(): pass\n")
        (tmp_path / "file2.py").write_text("def bar(): pass\n")

        args = MagicMock()
        args.path = str(tmp_path)
        args.git = False
        args.staged = False

        config = Config()
        files, target = collect_files_to_analyze(args, config)

        assert len(files) == 2

    def test_collect_nonexistent_path(self):
        """Test error on nonexistent path."""
        args = MagicMock()
        args.path = "/nonexistent/path"
        args.git = False
        args.staged = False

        config = Config()
        with pytest.raises(SystemExit):
            collect_files_to_analyze(args, config)


class TestRunAnalysis:
    """Tests for run_analysis function."""

    def test_run_analysis_no_issues(self, tmp_path):
        """Test analysis with clean code."""
        test_file = tmp_path / "clean.py"
        test_file.write_text("def foo():\n    pass\n")

        config = Config()
        issues = run_analysis([str(test_file)], config)

        assert len(issues) == 0

    def test_run_analysis_with_issues(self, tmp_path):
        """Test analysis with issues."""
        test_file = tmp_path / "long.py"
        # Create a long function
        lines = ["def long_func():\n"] + ["    x = 1\n"] * 35
        test_file.write_text("".join(lines))

        config = Config()
        issues = run_analysis([str(test_file)], config)

        assert len(issues) >= 1


class TestOutputResults:
    """Tests for output_results function."""

    def test_output_json(self, sample_issues, capsys):
        """Test JSON output."""
        args = MagicMock()
        args.format = "json"
        args.explain = False
        args.explain_summary = False

        config = Config()
        output_results(sample_issues, args, config, Path("."))

        captured = capsys.readouterr()
        assert '"summary"' in captured.out
        assert '"issues"' in captured.out

    def test_output_text(self, sample_issues, capsys):
        """Test text output."""
        args = MagicMock()
        args.format = "text"
        args.explain = False
        args.explain_summary = False

        config = Config()
        output_results(sample_issues, args, config, Path("test.py"))

        captured = capsys.readouterr()
        assert "[CRITICAL]" in captured.out


class TestPrintIssuesWithExplanations:
    """Tests for print_issues_with_explanations function."""

    def test_verbose_explanations(self, sample_issues, capsys):
        """Test verbose explanations."""
        print_issues_with_explanations(sample_issues, verbose=True, summary=False)

        captured = capsys.readouterr()
        assert "Why it matters" in captured.out or "explanation" in captured.out.lower()

    def test_summary_explanations(self, sample_issues, capsys):
        """Test summary explanations."""
        print_issues_with_explanations(sample_issues, verbose=False, summary=True)

        captured = capsys.readouterr()
        assert "issue" in captured.out.lower()

    def test_empty_issues(self, capsys):
        """Test with no issues."""
        print_issues_with_explanations([])

        captured = capsys.readouterr()
        assert "No issues" in captured.out


class TestAnalyzeSingleFile:
    """Tests for analyze_single_file function."""

    def test_analyze_clean_file(self, tmp_path):
        """Test analyzing a clean file."""
        test_file = tmp_path / "clean.py"
        test_file.write_text("def foo():\n    pass\n")

        config = Config()
        issues = analyze_single_file(test_file, config)

        assert len(issues) == 0


class TestAnalyzeDirectory:
    """Tests for analyze_directory function."""

    def test_analyze_empty_directory(self, tmp_path, capsys):
        """Test analyzing empty directory."""
        config = Config()
        issues = analyze_directory(tmp_path, config)

        captured = capsys.readouterr()
        assert "No Python files" in captured.out
        assert issues == []

    def test_analyze_directory_with_files(self, tmp_path):
        """Test analyzing directory with files."""
        (tmp_path / "test.py").write_text("def foo():\n    pass\n")

        config = Config()
        issues = analyze_directory(tmp_path, config)

        # Clean file, no issues
        assert issues == []


class TestCreateArgumentParser:
    """Tests for argument parser creation."""

    def test_all_arguments_exist(self):
        """Test that all expected arguments exist."""
        parser = create_argument_parser()

        # Parse empty args (using defaults)
        args = parser.parse_args([])

        # Check V6-V10 flags exist
        assert hasattr(args, "ai_suggestions")
        assert hasattr(args, "apply")
        assert hasattr(args, "project")
        assert hasattr(args, "git")
        assert hasattr(args, "plan")

    def test_ai_provider_choices(self):
        """Test AI provider choices."""
        parser = create_argument_parser()

        args = parser.parse_args(["--ai-provider", "openai"])
        assert args.ai_provider == "openai"

        args = parser.parse_args(["--ai-provider", "anthropic"])
        assert args.ai_provider == "anthropic"

    def test_plan_format_choices(self):
        """Test plan format choices."""
        parser = create_argument_parser()

        args = parser.parse_args(["--plan-format", "markdown"])
        assert args.plan_format == "markdown"
