"""Refactor Planner module for V10.

This module aggregates analysis results and prioritization to generate
strategic refactoring plans.
"""

from dataclasses import dataclass
from typing import List, Optional

from .analyzer import Issue, Severity
from .project_analyzer import ProjectAnalysis


@dataclass
class PlanMetric:
    """Metric for the refactoring plan."""

    total_files: int = 0
    total_functions: int = 0
    total_issues: int = 0
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    duplicate_count: int = 0
    average_complexity_score: float = 0.0


@dataclass
class RefactorItem:
    """A single item in the refactoring plan."""

    priority_score: float
    issue: Issue
    file_path: str
    function_name: str
    description: str
    effort: str  # "Low", "Medium", "High"
    impact: str  # "Low", "Medium", "High"

    def __lt__(self, other):
        return self.priority_score > other.priority_score  # Higher score first


@dataclass
class RefactorPlan:
    """Complete refactoring plan."""

    executive_summary: str
    metrics: PlanMetric
    critical_hotspots: List[RefactorItem]
    quick_wins: List[RefactorItem]
    strategic_roadmap: List[str]
    llm_advice: Optional[str] = None


class RefactorPlanner:
    """Planner to generate strategic refactoring roadmaps."""

    def __init__(self, issues: List[Issue], project_analysis: Optional[ProjectAnalysis] = None):
        self.issues = issues
        self.project_analysis = project_analysis
        self.metrics = self._calculate_metrics()

    def generate_plan(self) -> RefactorPlan:
        """Generate the full refactoring plan."""
        items = self._prioritize_issues()
        hotspots = sorted(items, key=lambda x: x.priority_score, reverse=True)[:5]
        quick_wins = self._identify_quick_wins(items)

        return RefactorPlan(
            executive_summary=self._generate_summary(),
            metrics=self.metrics,
            critical_hotspots=hotspots,
            quick_wins=quick_wins,
            strategic_roadmap=self._generate_roadmap(hotspots, quick_wins),
        )

    def _calculate_metrics(self) -> PlanMetric:
        """Calculate high-level metrics."""
        files = {issue.file for issue in self.issues}
        functions = {f"{issue.file}:{issue.function_name}" for issue in self.issues}

        critical = sum(1 for i in self.issues if i.severity == Severity.CRITICAL)
        warn = sum(1 for i in self.issues if i.severity == Severity.WARN)
        info = sum(1 for i in self.issues if i.severity == Severity.INFO)

        duplicates = len(self.project_analysis.duplicates) if self.project_analysis else 0

        # Simple health score (lower is better, used for avg complexity proxy)
        total_score = (critical * 10) + (warn * 3) + (info * 1)
        avg_score = total_score / len(functions) if functions else 0.0

        return PlanMetric(
            total_files=len(files),
            total_functions=len(functions),
            total_issues=len(self.issues),
            critical_count=critical,
            warning_count=warn,
            info_count=info,
            duplicate_count=duplicates,
            average_complexity_score=avg_score,
        )

    def _prioritize_issues(self) -> List[RefactorItem]:
        """Score and prioritize all issues."""
        items = []
        for issue in self.issues:
            score = 0.0
            effort = "Medium"
            impact = "Low"

            # Base score by severity
            if issue.severity == Severity.CRITICAL:
                score += 100
                impact = "High"
                effort = "High"
            elif issue.severity == Severity.WARN:
                score += 50
                impact = "Medium"
            else:
                score += 10

            # Adjust by rule type
            if issue.rule_name == "deep-nesting":
                score *= 1.2  # Harder to read
                effort = "High"
            elif issue.rule_name == "too-many-parameters":
                score *= 1.1  # Interface complexity
                effort = "Medium"

            # Simple Quick Win detection (Short function but critical logic? No.)
            # Quick wins are usually simple style fixes or small refactors.
            # Here we define Quick Win as INFO level or small params/length violation
            details = issue.details or {}
            is_quick_win = issue.severity == Severity.INFO or (
                issue.rule_name == "function-too-long"
                and details.get("length", 0) < 40  # Not massive
            )

            if is_quick_win:
                effort = "Low"

            items.append(
                RefactorItem(
                    priority_score=score,
                    issue=issue,
                    file_path=issue.file,
                    function_name=issue.function_name,
                    description=issue.message,
                    effort=effort,
                    impact=impact,
                )
            )

        return items

    def _identify_quick_wins(self, items: List[RefactorItem]) -> List[RefactorItem]:
        """Identify low-effort, high-enough-value items."""
        # Filter for Low effort
        low_effort = [i for i in items if i.effort == "Low"]
        # Sort by score (higher is better even for low effort)
        return sorted(low_effort, key=lambda x: x.priority_score, reverse=True)[:5]

    def _generate_summary(self) -> str:
        """Generate executive summary text."""
        total = self.metrics.total_issues
        health = "Good"
        if self.metrics.critical_count > 0:
            health = "Needs Attention"
        if self.metrics.critical_count > 10:
            health = "Critical"

        return (
            f"Analyzed {self.metrics.total_files} files. "
            f"Found {total} issues. Codebase Health: {health}."
        )

    def _generate_roadmap(
        self, hotspots: List[RefactorItem], quick_wins: List[RefactorItem]
    ) -> List[str]:
        """Generate a step-by-step roadmap."""
        roadmap = []

        if self.project_analysis and self.project_analysis.duplicates:
            roadmap.append(
                f"Phase 1: Architecture - Consolidate {len(self.project_analysis.duplicates)} duplicate groups."
            )

        if quick_wins:
            roadmap.append(
                f"Phase 2: Quick Wins - Fix {len(quick_wins)} low-effort issues to build momentum."
            )

        if hotspots:
            roadmap.append("Phase 3: Deep Dives - Refactor the top critical hotspots.")

        roadmap.append("Phase 4: Maintenance - Address remaining lower priority warnings.")

        return roadmap

    def format_plan(self, plan: RefactorPlan, format_type: str = "text") -> str:
        """Format the plan as a string."""
        if format_type == "markdown":
            return self._format_markdown(plan)
        return self._format_text(plan)

    def _format_markdown(self, plan: RefactorPlan) -> str:
        md = ["# 🏗️ Refactoring Plan", "", f"**{plan.executive_summary}**", ""]

        # Metrics Table
        md.append("## 📊 Metrics")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| Files Analyzed | {plan.metrics.total_files} |")
        md.append(f"| Critical Issues | {plan.metrics.critical_count} 🔴 |")
        md.append(f"| Warnings | {plan.metrics.warning_count} 🟡 |")
        md.append(f"| Duplicates | {plan.metrics.duplicate_count} 🔄 |")
        md.append("")

        # Roadmap
        md.append("## 🛣️ Strategic Roadmap")
        for step in plan.strategic_roadmap:
            md.append(f"- {step}")
        md.append("")

        # Hotspots
        md.append("## 🔥 Top 5 Critical Hotspots")
        for item in plan.critical_hotspots:
            md.append(f"### {item.function_name} ({item.file_path})")
            md.append(f"- **Impact:** {item.impact} | **Effort:** {item.effort}")
            md.append(f"- {item.description}")
            md.append("")

        # Quick Wins
        md.append("## ⚡ Quick Wins")
        for item in plan.quick_wins:
            md.append(f"- **{item.function_name}**: {item.description}")

        if plan.llm_advice:
            md.append("")
            md.append("## 🤖 AI Strategic Advice")
            md.append(plan.llm_advice)

        return "\n".join(md)

    def _format_text(self, plan: RefactorPlan) -> str:
        lines = ["\n[REFACTORING PLAN]", "=" * 50, plan.executive_summary, "-" * 50]

        lines.append(
            f"Critical: {plan.metrics.critical_count} | Warnings: {plan.metrics.warning_count}"
        )
        lines.append(f"Duplicates: {plan.metrics.duplicate_count}\n")

        lines.append("STRATEGIC ROADMAP:")
        for step in plan.strategic_roadmap:
            lines.append(f"  • {step}")
        lines.append("")

        lines.append("TOP 5 HOTSPOTS:")
        for item in plan.critical_hotspots:
            lines.append(f"  • {item.function_name} ({item.file_path}) - {item.impact} Impact")

        lines.append("\nQUICK WINS:")
        for item in plan.quick_wins:
            lines.append(f"  • {item.function_name}: {item.description}")

        if plan.llm_advice:
            lines.append("\nAI STRATEGIC ADVICE:")
            lines.append(plan.llm_advice)

        return "\n".join(lines)
