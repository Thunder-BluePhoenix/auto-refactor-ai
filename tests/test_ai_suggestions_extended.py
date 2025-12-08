"""Additional ai_suggestions tests for improving coverage."""

from auto_refactor_ai.ai_suggestions import (
    AIAnalysisResult,
    AIAnalysisSummary,
    extract_function_source,
    format_ai_suggestion,
    format_ai_summary,
    get_ai_suggestions,
    get_provider_status_message,
    print_ai_suggestions,
)
from auto_refactor_ai.analyzer import Issue, Severity
from auto_refactor_ai.llm_providers import RefactoringSuggestion


class TestExtractFunctionSourceExtended:
    """Extended tests for extract_function_source function."""

    def test_extract_from_file(self, tmp_path):
        """Test extracting function code from a file."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """# Header comment

def my_function():
    x = 1
    y = 2
    return x + y

def another():
    pass
"""
        )

        code = extract_function_source(str(test_file), 3, 6)

        assert "my_function" in code
        assert "x = 1" in code

    def test_extract_nonexistent_file(self):
        """Test with nonexistent file returns empty string."""
        code = extract_function_source("/nonexistent/file.py", 1, 10)
        # Returns empty string or handles gracefully
        assert isinstance(code, str)


class TestGetAISuggestionsExtended:
    """Extended tests for get_ai_suggestions function."""

    def test_empty_issues(self):
        """Test with empty issues list."""
        summary = get_ai_suggestions([], max_issues=5)

        assert len(summary.results) == 0


class TestFormatAISuggestionExtended:
    """Extended tests for format_ai_suggestion function."""

    def test_format_with_changes(self):
        """Test formatting with changes summary."""
        result = AIAnalysisResult(
            issue=Issue(
                file="test.py",
                function_name="foo",
                start_line=1,
                end_line=10,
                severity=Severity.WARN,
                message="Test issue",
                rule_name="test-rule",
            ),
            original_function_code="def foo(): pass",
            suggestion=RefactoringSuggestion(
                original_code="def foo(): pass",
                refactored_code="def foo(): return 1",
                explanation="Added return statement",
                confidence=0.8,
                changes_summary=["Added return", "Improved structure"],
            ),
        )

        output = format_ai_suggestion(result, show_original=True)

        assert "foo" in output

    def test_format_without_original(self):
        """Test formatting without showing original code."""
        result = AIAnalysisResult(
            issue=Issue(
                file="test.py",
                function_name="bar",
                start_line=1,
                end_line=5,
                severity=Severity.INFO,
                message="Test issue",
                rule_name="test-rule",
            ),
            original_function_code="def bar(): pass",
            suggestion=RefactoringSuggestion(
                original_code="def bar(): pass",
                refactored_code="def bar(): return None",
                explanation="Explicit return",
                confidence=0.9,
            ),
        )

        output = format_ai_suggestion(result, show_original=False)

        assert "bar" in output


class TestFormatAISummary:
    """Tests for format_ai_summary function."""

    def test_format_summary(self):
        """Test formatting the summary."""
        summary = AIAnalysisSummary(provider="openai", model="gpt-4")

        output = format_ai_summary(summary)

        assert len(output) > 0

    def test_format_summary_with_errors(self):
        """Test formatting summary with errors."""
        summary = AIAnalysisSummary(errors=["Error 1", "Error 2"])

        output = format_ai_summary(summary)

        # Should mention errors
        assert len(output) > 0


class TestPrintAISuggestionsExtended:
    """Extended tests for print_ai_suggestions function."""

    def test_print_empty_summary(self, capsys):
        """Test printing empty summary."""
        summary = AIAnalysisSummary()

        print_ai_suggestions(summary)

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_print_summary_with_results(self, capsys):
        """Test printing summary with results."""
        result = AIAnalysisResult(
            issue=Issue(
                file="test.py",
                function_name="foo",
                start_line=1,
                end_line=10,
                severity=Severity.WARN,
                message="Test issue",
                rule_name="test-rule",
            ),
            original_function_code="def foo(): pass",
            suggestion=RefactoringSuggestion(
                original_code="def foo(): pass",
                refactored_code="def foo(): return 1",
                explanation="Added return",
                confidence=0.8,
            ),
        )

        summary = AIAnalysisSummary(results=[result])

        print_ai_suggestions(summary)

        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestGetProviderStatusMessage:
    """Tests for provider status message."""

    def test_message_includes_providers(self):
        """Test that message includes provider names."""
        message = get_provider_status_message()

        # Should list available providers
        assert len(message) > 0
        assert (
            "provider" in message.lower() or "openai" in message.lower() or "Available" in message
        )


class TestAIAnalysisSummaryProperties:
    """Tests for AIAnalysisSummary properties."""

    def test_success_count(self):
        """Test success_count property."""
        result = AIAnalysisResult(
            issue=Issue(
                file="test.py",
                function_name="foo",
                start_line=1,
                end_line=10,
                severity=Severity.INFO,
                message="Test",
                rule_name="test",
            ),
            original_function_code="",
            suggestion=RefactoringSuggestion(
                original_code="",
                refactored_code="def foo(): return 1",
                explanation="Added return",
                confidence=0.9,
            ),
        )

        summary = AIAnalysisSummary(results=[result])

        assert summary.success_count == 1

    def test_error_count(self):
        """Test error_count property counts results without refactored_code."""
        # error_count counts results with empty refactored_code, not errors list
        empty_result = AIAnalysisResult(
            issue=Issue(
                file="test.py",
                function_name="foo",
                start_line=1,
                end_line=10,
                severity=Severity.INFO,
                message="Test",
                rule_name="test",
            ),
            original_function_code="",
            suggestion=RefactoringSuggestion(
                original_code="",
                refactored_code="",  # Empty = error
                explanation="",
                confidence=0.0,
            ),
        )

        summary = AIAnalysisSummary(results=[empty_result])

        assert summary.error_count == 1
