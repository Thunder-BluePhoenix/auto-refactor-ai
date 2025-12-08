"""V10 Refactor Planner extended tests."""

from unittest.mock import MagicMock, patch

import pytest

from auto_refactor_ai.analyzer import Issue, Severity
from auto_refactor_ai.refactor_planner import (
    RefactorPlanner,
)


@pytest.fixture
def sample_issues():
    """Create sample issues for testing."""
    return [
        Issue(
            file="main.py",
            function_name="long_function",
            start_line=1,
            end_line=100,
            severity=Severity.CRITICAL,
            message="Function is 100 lines long",
            rule_name="function-too-long",
            details={"length": 100},
        ),
        Issue(
            file="utils.py",
            function_name="helper",
            start_line=1,
            end_line=20,
            severity=Severity.WARN,
            message="Too many parameters (8)",
            rule_name="too-many-parameters",
            details={"params": 8},
        ),
        Issue(
            file="api.py",
            function_name="simple_fix",
            start_line=1,
            end_line=10,
            severity=Severity.INFO,
            message="Minor style issue",
            rule_name="style-issue",
        ),
    ]


class TestRefactorPlannerV10:
    """Tests for V10 RefactorPlanner features."""

    def test_generate_plan_without_llm(self, sample_issues):
        """Test plan generation without LLM advice."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan(include_llm_advice=False)

        assert plan.executive_summary != ""
        assert plan.metrics.total_issues == 3
        assert plan.llm_advice is None

    def test_generate_plan_with_llm_unavailable(self, sample_issues):
        """Test plan generation when LLM is unavailable."""
        with patch("auto_refactor_ai.refactor_planner.get_provider") as mock_provider:
            mock_provider.return_value.is_available.return_value = False

            planner = RefactorPlanner(sample_issues)
            plan = planner.generate_plan(include_llm_advice=True)

            assert plan.llm_advice is None

    def test_generate_plan_with_llm_success(self, sample_issues):
        """Test plan generation with successful LLM response."""
        with patch("auto_refactor_ai.refactor_planner.get_provider") as mock_get:
            mock_provider = MagicMock()
            mock_provider.is_available.return_value = True
            mock_provider.generate.return_value = MagicMock(
                success=True, content="Focus on long_function first. It's the critical bottleneck."
            )
            mock_get.return_value = mock_provider

            planner = RefactorPlanner(sample_issues)
            plan = planner.generate_plan(include_llm_advice=True)

            assert plan.llm_advice is not None
            assert "long_function" in plan.llm_advice


class TestFormatHtml:
    """Tests for HTML report generation."""

    def test_format_html_basic(self, sample_issues):
        """Test basic HTML formatting."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()

        html = planner.format_plan(plan, format_type="html")

        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "Refactoring Plan" in html
        assert "</html>" in html

    def test_format_html_includes_metrics(self, sample_issues):
        """Test HTML includes metrics."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()

        html = planner.format_plan(plan, format_type="html")

        assert "metric" in html
        assert str(plan.metrics.critical_count) in html

    def test_format_html_includes_hotspots(self, sample_issues):
        """Test HTML includes hotspots."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()

        html = planner.format_plan(plan, format_type="html")

        assert "hotspot" in html
        assert "long_function" in html

    def test_format_html_with_llm_advice(self, sample_issues):
        """Test HTML includes LLM advice section."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()
        plan.llm_advice = "Test AI advice content"

        html = planner.format_plan(plan, format_type="html")

        assert "ai-advice" in html
        assert "Test AI advice content" in html


class TestBuildLLMContext:
    """Tests for LLM context building."""

    def test_build_context(self, sample_issues):
        """Test LLM context generation."""
        planner = RefactorPlanner(sample_issues)
        items = planner._prioritize_issues()
        hotspots = sorted(items, key=lambda x: x.priority_score, reverse=True)[:5]
        quick_wins = planner._identify_quick_wins(items)

        context = planner._build_llm_context(hotspots, quick_wins)

        assert "Codebase Analysis Summary" in context
        assert "Critical Hotspots" in context
        assert "Quick Win" in context


class TestCLIOutputFlag:
    """Tests for CLI --output flag."""

    def test_output_to_file(self, tmp_path):
        """Test saving report to file."""
        from auto_refactor_ai.cli import handle_refactor_plan
        from auto_refactor_ai.config import Config

        test_file = tmp_path / "test.py"
        test_file.write_text("def foo():\n    pass\n")

        output_file = tmp_path / "report.html"

        args = MagicMock()
        args.path = str(tmp_path)
        args.min_lines = 5
        args.similarity_threshold = 0.8
        args.ai_suggestions = False
        args.ai_provider = None
        args.ai_model = None
        args.plan_format = "html"
        args.output = str(output_file)

        config = Config()
        issues = []  # Empty issues for quick test

        handle_refactor_plan(args, config, issues)

        assert output_file.exists()
        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
