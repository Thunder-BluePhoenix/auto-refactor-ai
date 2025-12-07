"""AI-powered code refactoring suggestions.

This module provides AI-powered suggestions for fixing code issues
by integrating with LLM providers to generate refactored code.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

from .analyzer import Issue, Severity
from .llm_providers import (
    get_provider,
    LLMConfig,
    LLMProvider,
    RefactoringSuggestion,
    check_provider_availability,
)


@dataclass
class AIAnalysisResult:
    """Result of AI analysis for a single issue."""
    issue: Issue
    suggestion: RefactoringSuggestion
    original_function_code: str
    tokens_used: int = 0
    cost_estimate: float = 0.0


@dataclass
class AIAnalysisSummary:
    """Summary of AI analysis for all issues."""
    results: List[AIAnalysisResult] = field(default_factory=list)
    total_tokens: int = 0
    total_cost: float = 0.0
    provider: str = ""
    model: str = ""
    errors: List[str] = field(default_factory=list)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.suggestion.refactored_code)

    @property
    def error_count(self) -> int:
        return len(self.results) - self.success_count


def extract_function_source(file_path: str, start_line: int, end_line: int) -> str:
    """Extract function source code from a file.

    Args:
        file_path: Path to the Python file
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)

    Returns:
        The source code of the function
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Extract lines (convert to 0-indexed)
        func_lines = lines[start_line - 1 : end_line]
        return "".join(func_lines)
    except Exception as e:
        return f"# Error extracting function: {e}"


def get_ai_suggestions(
    issues: List[Issue],
    config: Optional[LLMConfig] = None,
    max_issues: int = 5,
    skip_info: bool = True,
) -> AIAnalysisSummary:
    """Get AI suggestions for a list of issues.

    Args:
        issues: List of code issues to analyze
        config: LLM configuration (auto-detected if None)
        max_issues: Maximum number of issues to process
        skip_info: Skip INFO-level issues

    Returns:
        Summary with all AI suggestions
    """
    provider = get_provider(config)
    summary = AIAnalysisSummary(
        provider=provider.config.provider.value,
        model=provider.config.model,
    )

    # Check if provider is available
    if not provider.is_available():
        summary.errors.append(
            f"LLM provider '{provider.config.provider.value}' is not available. "
            "Please set the appropriate API key environment variable."
        )
        return summary

    # Filter and limit issues
    filtered_issues = issues
    if skip_info:
        filtered_issues = [i for i in issues if i.severity != Severity.INFO]

    # Sort by severity (critical first)
    severity_order = {Severity.CRITICAL: 0, Severity.WARN: 1, Severity.INFO: 2}
    filtered_issues = sorted(
        filtered_issues,
        key=lambda x: severity_order[x.severity]
    )

    # Limit number of issues
    issues_to_process = filtered_issues[:max_issues]

    for issue in issues_to_process:
        try:
            # Extract the function source code
            original_code = extract_function_source(
                issue.file,
                issue.start_line,
                issue.end_line
            )

            # Get AI suggestion
            suggestion = provider.get_refactoring_suggestion(
                code=original_code,
                issue_type=issue.rule_name,
                issue_message=issue.message,
                function_name=issue.function_name,
            )

            result = AIAnalysisResult(
                issue=issue,
                suggestion=suggestion,
                original_function_code=original_code,
            )

            summary.results.append(result)

        except Exception as e:
            summary.errors.append(f"Error processing {issue.function_name}: {str(e)}")

    return summary


def format_ai_suggestion(result: AIAnalysisResult, show_original: bool = True) -> str:
    """Format an AI suggestion for display.

    Args:
        result: The AI analysis result
        show_original: Whether to show the original code

    Returns:
        Formatted string for display
    """
    lines = []

    # Header
    lines.append("\n" + "=" * 80)
    lines.append(f"🤖 AI REFACTORING SUGGESTION")
    lines.append("=" * 80)
    lines.append(f"File: {result.issue.file}:{result.issue.start_line}-{result.issue.end_line}")
    lines.append(f"Function: {result.issue.function_name}()")
    lines.append(f"Issue: {result.issue.rule_name} ({result.issue.severity.value})")
    lines.append(f"Problem: {result.issue.message}")
    lines.append("-" * 80)

    if show_original:
        lines.append("\n📝 ORIGINAL CODE:")
        lines.append("-" * 40)
        lines.append("```python")
        lines.append(result.original_function_code.rstrip())
        lines.append("```")

    if result.suggestion.refactored_code:
        lines.append("\n✨ SUGGESTED REFACTORING:")
        lines.append("-" * 40)
        lines.append("```python")
        lines.append(result.suggestion.refactored_code.rstrip())
        lines.append("```")

        if result.suggestion.explanation:
            lines.append("\n💡 EXPLANATION:")
            lines.append("-" * 40)
            lines.append(result.suggestion.explanation)

        if result.suggestion.changes_summary:
            lines.append("\n📋 CHANGES MADE:")
            lines.append("-" * 40)
            for change in result.suggestion.changes_summary:
                lines.append(f"  • {change}")

        lines.append(f"\n🎯 Confidence: {result.suggestion.confidence:.0%}")

    else:
        lines.append("\n❌ Could not generate suggestion")
        if result.suggestion.explanation:
            lines.append(f"   Reason: {result.suggestion.explanation}")

    lines.append("\n" + "=" * 80)

    return "\n".join(lines)


def format_ai_summary(summary: AIAnalysisSummary) -> str:
    """Format the AI analysis summary.

    Args:
        summary: The AI analysis summary

    Returns:
        Formatted string for display
    """
    lines = []

    lines.append("\n" + "=" * 80)
    lines.append("🤖 AI ANALYSIS SUMMARY")
    lines.append("=" * 80)
    lines.append(f"Provider: {summary.provider}")
    lines.append(f"Model: {summary.model}")
    lines.append(f"Issues Analyzed: {len(summary.results)}")
    lines.append(f"Successful Suggestions: {summary.success_count}")
    lines.append(f"Failed: {summary.error_count}")

    if summary.total_tokens > 0:
        lines.append(f"Total Tokens: {summary.total_tokens}")
    if summary.total_cost > 0:
        lines.append(f"Estimated Cost: ${summary.total_cost:.4f}")

    if summary.errors:
        lines.append("\n⚠️  Errors:")
        for error in summary.errors:
            lines.append(f"   • {error}")

    lines.append("=" * 80 + "\n")

    return "\n".join(lines)


def print_ai_suggestions(summary: AIAnalysisSummary, show_original: bool = True) -> None:
    """Print all AI suggestions to stdout.

    Args:
        summary: The AI analysis summary
        show_original: Whether to show original code
    """
    if not summary.results and not summary.errors:
        print("\n✓ No issues to analyze!\n")
        return

    if summary.errors and not summary.results:
        print(format_ai_summary(summary))
        return

    # Print each suggestion
    for result in summary.results:
        print(format_ai_suggestion(result, show_original))

    # Print summary
    print(format_ai_summary(summary))


def get_provider_status_message() -> str:
    """Get a status message about available providers."""
    availability = check_provider_availability()

    lines = ["\n🔧 LLM Provider Status:"]

    env_vars = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "ollama": "(local)",
    }

    for provider, available in availability.items():
        status = "✅" if available else "❌"
        env_var = env_vars.get(provider, "")
        lines.append(f"  {status} {provider.capitalize()}: {'Available' if available else f'Not configured ({env_var})'}")

    return "\n".join(lines)
