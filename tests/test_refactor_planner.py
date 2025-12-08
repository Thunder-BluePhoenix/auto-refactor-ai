"""Tests for the RefactorPlanner module (V10)."""

import pytest

from auto_refactor_ai.analyzer import Issue, Severity
from auto_refactor_ai.project_analyzer import DuplicateGroup, FunctionSignature, ProjectAnalysis
from auto_refactor_ai.refactor_planner import (
    PlanMetric,
    RefactorItem,
    RefactorPlan,
    RefactorPlanner,
)


@pytest.fixture
def sample_issues():
    """Create sample issues for testing."""
    return [
        Issue(
            file="file1.py",
            function_name="process_data",
            start_line=10,
            end_line=80,
            severity=Severity.CRITICAL,
            message="Function too long",
            rule_name="function-too-long",
            details={"length": 70, "max_length": 30},
        ),
        Issue(
            file="file1.py",
            function_name="validate_input",
            start_line=100,
            end_line=120,
            severity=Severity.WARN,
            message="Too many parameters",
            rule_name="too-many-parameters",
            details={"params": 7, "max_params": 5},
        ),
        Issue(
            file="file2.py",
            function_name="calculate",
            start_line=1,
            end_line=35,
            severity=Severity.INFO,
            message="Function too long",
            rule_name="function-too-long",
            details={"length": 35, "max_length": 30},
        ),
    ]


@pytest.fixture
def sample_project_analysis():
    """Create sample ProjectAnalysis for testing."""
    analysis = ProjectAnalysis(root_path="./test_project")
    analysis.files_analyzed = 3
    analysis.functions_found = 10

    # Add a duplicate group
    func1 = FunctionSignature(
        file="file1.py",
        name="helper_a",
        start_line=1,
        end_line=10,
        parameters=["x"],
        body_hash="abc123",
        parameter_count=1,
        line_count=10,
    )
    func2 = FunctionSignature(
        file="file2.py",
        name="helper_b",
        start_line=1,
        end_line=10,
        parameters=["y"],
        body_hash="abc123",
        parameter_count=1,
        line_count=10,
    )
    duplicate = DuplicateGroup(functions=[func1, func2], similarity=1.0)
    analysis.duplicates = [duplicate]

    return analysis


class TestPlanMetric:
    """Tests for PlanMetric dataclass."""

    def test_plan_metric_defaults(self):
        """Test PlanMetric default values."""
        metric = PlanMetric()
        assert metric.total_files == 0
        assert metric.total_functions == 0
        assert metric.total_issues == 0
        assert metric.critical_count == 0
        assert metric.warning_count == 0
        assert metric.info_count == 0
        assert metric.duplicate_count == 0
        assert metric.average_complexity_score == 0.0

    def test_plan_metric_with_values(self):
        """Test PlanMetric with custom values."""
        metric = PlanMetric(
            total_files=5, critical_count=2, warning_count=3, average_complexity_score=7.5
        )
        assert metric.total_files == 5
        assert metric.critical_count == 2
        assert metric.warning_count == 3
        assert metric.average_complexity_score == 7.5


class TestRefactorItem:
    """Tests for RefactorItem dataclass."""

    def test_refactor_item_creation(self, sample_issues):
        """Test RefactorItem creation."""
        issue = sample_issues[0]
        item = RefactorItem(
            priority_score=100.0,
            issue=issue,
            file_path=issue.file,
            function_name=issue.function_name,
            description=issue.message,
            effort="High",
            impact="High",
        )
        assert item.priority_score == 100.0
        assert item.effort == "High"
        assert item.impact == "High"

    def test_refactor_item_comparison(self, sample_issues):
        """Test RefactorItem comparison (higher priority first)."""
        issue = sample_issues[0]
        item1 = RefactorItem(
            priority_score=100.0,
            issue=issue,
            file_path="f.py",
            function_name="fn",
            description="msg",
            effort="High",
            impact="High",
        )
        item2 = RefactorItem(
            priority_score=50.0,
            issue=issue,
            file_path="f.py",
            function_name="fn",
            description="msg",
            effort="Low",
            impact="Low",
        )
        # __lt__ returns True when self.priority_score > other.priority_score
        assert item1 < item2  # 100 > 50, so item1 should come first in sorting


class TestRefactorPlanner:
    """Tests for RefactorPlanner class."""

    def test_init_with_issues(self, sample_issues):
        """Test planner initialization with issues."""
        planner = RefactorPlanner(sample_issues)
        assert planner.issues == sample_issues
        assert planner.project_analysis is None
        assert planner.metrics is not None

    def test_init_with_project_analysis(self, sample_issues, sample_project_analysis):
        """Test planner initialization with project analysis."""
        planner = RefactorPlanner(sample_issues, sample_project_analysis)
        assert planner.project_analysis == sample_project_analysis

    def test_calculate_metrics(self, sample_issues):
        """Test metrics calculation."""
        planner = RefactorPlanner(sample_issues)
        metrics = planner.metrics

        assert metrics.total_files == 2  # file1.py, file2.py
        assert metrics.total_functions == 3
        assert metrics.total_issues == 3
        assert metrics.critical_count == 1
        assert metrics.warning_count == 1
        assert metrics.info_count == 1
        assert metrics.duplicate_count == 0  # No project analysis

    def test_calculate_metrics_with_duplicates(self, sample_issues, sample_project_analysis):
        """Test metrics calculation with duplicates."""
        planner = RefactorPlanner(sample_issues, sample_project_analysis)
        metrics = planner.metrics

        assert metrics.duplicate_count == 1  # One duplicate group

    def test_generate_plan_returns_refactor_plan(self, sample_issues):
        """Test that generate_plan returns a RefactorPlan."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()

        assert isinstance(plan, RefactorPlan)
        assert isinstance(plan.executive_summary, str)
        assert isinstance(plan.metrics, PlanMetric)
        assert isinstance(plan.critical_hotspots, list)
        assert isinstance(plan.quick_wins, list)
        assert isinstance(plan.strategic_roadmap, list)

    def test_generate_plan_hotspots(self, sample_issues):
        """Test that critical issues appear in hotspots."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()

        # Should have hotspots (up to 5)
        assert len(plan.critical_hotspots) <= 5
        assert len(plan.critical_hotspots) > 0

        # Critical issue should be in hotspots
        function_names = [item.function_name for item in plan.critical_hotspots]
        assert "process_data" in function_names

    def test_generate_plan_quick_wins(self, sample_issues):
        """Test that low-effort issues appear in quick wins."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()

        # The INFO level issue with < 40 lines is a quick win
        quick_win_names = [item.function_name for item in plan.quick_wins]
        assert "calculate" in quick_win_names

    def test_generate_plan_roadmap(self, sample_issues):
        """Test that roadmap is generated."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()

        assert len(plan.strategic_roadmap) > 0
        # Should contain phases
        roadmap_text = " ".join(plan.strategic_roadmap)
        assert "Phase" in roadmap_text

    def test_format_plan_text(self, sample_issues):
        """Test text formatting."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()
        text = planner.format_plan(plan, "text")

        assert "[REFACTORING PLAN]" in text
        assert "STRATEGIC ROADMAP:" in text
        assert "TOP 5 HOTSPOTS:" in text
        assert "QUICK WINS:" in text

    def test_format_plan_markdown(self, sample_issues):
        """Test markdown formatting."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()
        md = planner.format_plan(plan, "markdown")

        assert "# 🏗️ Refactoring Plan" in md
        assert "## 📊 Metrics" in md
        assert "## 🛣️ Strategic Roadmap" in md
        assert "## 🔥 Top 5 Critical Hotspots" in md
        assert "## ⚡ Quick Wins" in md


class TestRefactorPlannerWithProjectAnalysis:
    """Tests for RefactorPlanner with ProjectAnalysis."""

    def test_roadmap_includes_duplicates(self, sample_issues, sample_project_analysis):
        """Test that roadmap includes duplicate consolidation phase."""
        planner = RefactorPlanner(sample_issues, sample_project_analysis)
        plan = planner.generate_plan()

        roadmap_text = " ".join(plan.strategic_roadmap)
        assert "Architecture" in roadmap_text or "duplicate" in roadmap_text.lower()

    def test_summary_generation(self, sample_issues):
        """Test executive summary generation."""
        planner = RefactorPlanner(sample_issues)
        plan = planner.generate_plan()

        assert "Analyzed" in plan.executive_summary
        assert "files" in plan.executive_summary.lower()
        assert "issues" in plan.executive_summary.lower()
