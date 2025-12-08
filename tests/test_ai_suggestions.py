"""Tests for AI suggestions module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

from auto_refactor_ai.ai_suggestions import (
    AIAnalysisResult,
    AIAnalysisSummary,
    extract_function_source,
    format_ai_suggestion,
    format_ai_summary,
    get_ai_suggestions,
    get_provider_status_message,
)
from auto_refactor_ai.analyzer import Issue, Severity
from auto_refactor_ai.llm_providers import (
    RefactoringSuggestion,
)


class TestAIAnalysisResult:
    """Tests for AIAnalysisResult dataclass."""

    def test_result_creation(self):
        """Test creating an AI analysis result."""
        issue = Issue(
            file="test.py",
            start_line=1,
            end_line=10,
            function_name="test_func",
            rule_name="function-too-long",
            message="Function is too long",
            severity=Severity.WARN,
        )
        suggestion = RefactoringSuggestion(
            original_code="def test(): pass",
            refactored_code="def test():\n    pass",
            explanation="Split function",
            confidence=0.8,
        )
        result = AIAnalysisResult(
            issue=issue,
            suggestion=suggestion,
            original_function_code="def test(): pass",
        )

        assert result.issue.function_name == "test_func"
        assert result.suggestion.confidence == 0.8


class TestAIAnalysisSummary:
    """Tests for AIAnalysisSummary dataclass."""

    def test_empty_summary(self):
        """Test empty summary."""
        summary = AIAnalysisSummary()
        assert summary.success_count == 0
        assert summary.error_count == 0
        assert summary.total_tokens == 0

    def test_summary_with_results(self):
        """Test summary with results."""
        issue = Issue(
            file="test.py",
            start_line=1,
            end_line=10,
            function_name="test",
            rule_name="test-rule",
            message="Test message",
            severity=Severity.WARN,
        )
        successful_suggestion = RefactoringSuggestion(
            original_code="code",
            refactored_code="new code",
            explanation="Fixed",
            confidence=0.8,
        )
        failed_suggestion = RefactoringSuggestion(
            original_code="code",
            refactored_code="",
            explanation="Failed",
            confidence=0.0,
        )

        summary = AIAnalysisSummary(
            results=[
                AIAnalysisResult(
                    issue=issue, suggestion=successful_suggestion, original_function_code="code"
                ),
                AIAnalysisResult(
                    issue=issue, suggestion=failed_suggestion, original_function_code="code"
                ),
            ],
            provider="openai",
            model="gpt-4o-mini",
        )

        assert summary.success_count == 1
        assert summary.error_count == 1


class TestExtractFunctionSource:
    """Tests for extract_function_source function."""

    def test_extract_function(self):
        """Test extracting function source from file."""
        code = """def foo():
    pass

def bar():
    return 42
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            # Extract first function (lines 1-2)
            source = extract_function_source(temp_path, 1, 2)
            assert "def foo():" in source
            assert "pass" in source

            # Extract second function (lines 4-5)
            source = extract_function_source(temp_path, 4, 5)
            assert "def bar():" in source
            assert "return 42" in source
        finally:
            os.unlink(temp_path)

    def test_extract_nonexistent_file(self):
        """Test extracting from nonexistent file."""
        source = extract_function_source("/nonexistent/path.py", 1, 10)
        assert "Error extracting function" in source


class TestGetAISuggestions:
    """Tests for get_ai_suggestions function."""

    def test_no_issues(self):
        """Test with no issues."""
        summary = get_ai_suggestions(issues=[])
        assert len(summary.results) == 0

    @patch("auto_refactor_ai.ai_suggestions.get_provider")
    def test_provider_not_available(self, mock_get_provider):
        """Test when provider is not available."""
        mock_provider = MagicMock()
        mock_provider.is_available.return_value = False
        mock_provider.config.provider.value = "openai"
        mock_get_provider.return_value = mock_provider

        issue = Issue(
            file="test.py",
            start_line=1,
            end_line=10,
            function_name="test",
            rule_name="test-rule",
            message="Test",
            severity=Severity.WARN,
        )

        summary = get_ai_suggestions(issues=[issue])
        assert len(summary.errors) > 0
        assert "not available" in summary.errors[0]

    def test_skip_info_issues(self):
        """Test that INFO issues are skipped by default."""
        # This tests the filtering logic
        info_issue = Issue(
            file="test.py",
            start_line=1,
            end_line=10,
            function_name="test",
            rule_name="test-rule",
            message="Test",
            severity=Severity.INFO,
        )

        # With skip_info=True (default), no issues should be processed
        # since we only have INFO issues
        with patch("auto_refactor_ai.ai_suggestions.get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.is_available.return_value = True
            mock_provider.config.provider.value = "openai"
            mock_provider.config.model = "test-model"
            mock_get_provider.return_value = mock_provider

            summary = get_ai_suggestions(issues=[info_issue], skip_info=True)
            # No suggestions should be generated for INFO issues
            assert len(summary.results) == 0


class TestFormatAISuggestion:
    """Tests for format_ai_suggestion function."""

    def test_format_successful_suggestion(self):
        """Test formatting a successful suggestion."""
        issue = Issue(
            file="test.py",
            start_line=1,
            end_line=10,
            function_name="test_func",
            rule_name="function-too-long",
            message="Function is too long",
            severity=Severity.WARN,
        )
        suggestion = RefactoringSuggestion(
            original_code="def test(): pass",
            refactored_code="def test():\n    pass",
            explanation="Split function",
            confidence=0.8,
            changes_summary=["Added newline"],
        )
        result = AIAnalysisResult(
            issue=issue,
            suggestion=suggestion,
            original_function_code="def test(): pass",
        )

        formatted = format_ai_suggestion(result)

        assert "AI REFACTORING SUGGESTION" in formatted
        assert "test.py:1-10" in formatted
        assert "test_func()" in formatted
        assert "ORIGINAL CODE" in formatted
        assert "SUGGESTED REFACTORING" in formatted
        assert "EXPLANATION" in formatted
        assert "80%" in formatted  # Confidence

    def test_format_failed_suggestion(self):
        """Test formatting a failed suggestion."""
        issue = Issue(
            file="test.py",
            start_line=1,
            end_line=10,
            function_name="test_func",
            rule_name="test-rule",
            message="Test",
            severity=Severity.WARN,
        )
        suggestion = RefactoringSuggestion(
            original_code="code",
            refactored_code="",
            explanation="API error",
            confidence=0.0,
        )
        result = AIAnalysisResult(
            issue=issue,
            suggestion=suggestion,
            original_function_code="code",
        )

        formatted = format_ai_suggestion(result)
        assert "Could not generate suggestion" in formatted


class TestFormatAISummary:
    """Tests for format_ai_summary function."""

    def test_format_summary(self):
        """Test formatting the summary."""
        summary = AIAnalysisSummary(
            provider="openai",
            model="gpt-4o-mini",
            total_tokens=1000,
            total_cost=0.01,
        )

        formatted = format_ai_summary(summary)

        assert "AI ANALYSIS SUMMARY" in formatted
        assert "openai" in formatted
        assert "gpt-4o-mini" in formatted

    def test_format_summary_with_errors(self):
        """Test formatting summary with errors."""
        summary = AIAnalysisSummary(
            provider="openai",
            model="gpt-4o-mini",
            errors=["Error 1", "Error 2"],
        )

        formatted = format_ai_summary(summary)
        assert "Errors" in formatted
        assert "Error 1" in formatted


class TestGetProviderStatusMessage:
    """Tests for get_provider_status_message function."""

    def test_status_message(self):
        """Test getting provider status message."""
        message = get_provider_status_message()
        assert "LLM Provider Status" in message
        assert "openai" in message.lower() or "Openai" in message
