"""Tests for explanations module (V5)."""

from auto_refactor_ai.analyzer import Issue, Severity
from auto_refactor_ai.explanations import (
    EXPLANATIONS,
    format_explanation,
    get_explanation,
    get_severity_guidance,
)


class TestGetExplanation:
    """Test get_explanation function."""

    def test_get_explanation_for_long_function(self):
        """Test getting explanation for function-too-long rule."""
        issue = Issue(
            severity=Severity.CRITICAL,
            file="test.py",
            function_name="long_func",
            start_line=1,
            end_line=100,
            rule_name="function-too-long",
            message="Function is too long",
        )

        explanation = get_explanation(issue)

        assert "Single Responsibility Principle" in explanation.why_it_matters
        assert len(explanation.how_to_fix) > 0
        assert "GOOD:" in explanation.good_example
        assert "BAD:" in explanation.bad_example
        assert len(explanation.references) > 0

    def test_get_explanation_for_too_many_parameters(self):
        """Test getting explanation for too-many-parameters rule."""
        issue = Issue(
            severity=Severity.WARN,
            file="test.py",
            function_name="many_params",
            start_line=1,
            end_line=10,
            rule_name="too-many-parameters",
            message="Too many parameters",
        )

        explanation = get_explanation(issue)

        assert "dataclass" in explanation.how_to_fix[0].lower()
        assert "configuration" in explanation.good_example.lower()
        assert len(explanation.references) > 0

    def test_get_explanation_for_deep_nesting(self):
        """Test getting explanation for deep-nesting rule."""
        issue = Issue(
            severity=Severity.CRITICAL,
            file="test.py",
            function_name="nested_func",
            start_line=1,
            end_line=50,
            rule_name="deep-nesting",
            message="Deep nesting detected",
        )

        explanation = get_explanation(issue)

        assert "guard clauses" in explanation.how_to_fix[0].lower()
        assert "early return" in explanation.good_example.lower()
        assert "cognitive complexity" in explanation.why_it_matters.lower()

    def test_get_explanation_for_unknown_rule(self):
        """Test getting explanation for unknown rule (default)."""
        issue = Issue(
            severity=Severity.INFO,
            file="test.py",
            function_name="func",
            start_line=1,
            end_line=10,
            rule_name="unknown-rule",
            message="Unknown issue",
        )

        explanation = get_explanation(issue)

        assert explanation.why_it_matters is not None
        assert len(explanation.how_to_fix) > 0
        assert explanation.good_example is not None
        assert explanation.bad_example is not None


class TestFormatExplanation:
    """Test format_explanation function."""

    def test_format_explanation_verbose(self):
        """Test formatting explanation in verbose mode."""
        issue = Issue(
            severity=Severity.CRITICAL,
            file="test.py",
            function_name="long_func",
            start_line=1,
            end_line=100,
            rule_name="function-too-long",
            message="Function is too long",
        )

        explanation = get_explanation(issue)
        formatted = format_explanation(issue, explanation, verbose=True)

        # Check all sections are present
        assert "EXPLANATION:" in formatted
        assert "WHY THIS MATTERS:" in formatted
        assert "HOW TO FIX:" in formatted
        assert "BAD EXAMPLE" in formatted
        assert "GOOD EXAMPLE" in formatted
        assert "FURTHER READING:" in formatted
        assert issue.file in formatted
        assert issue.function_name in formatted

    def test_format_explanation_summary(self):
        """Test formatting explanation in summary mode."""
        issue = Issue(
            severity=Severity.WARN,
            file="test.py",
            function_name="many_params",
            start_line=1,
            end_line=10,
            rule_name="too-many-parameters",
            message="Too many parameters",
        )

        explanation = get_explanation(issue)
        formatted = format_explanation(issue, explanation, verbose=False)

        # Summary should have quick fix but not detailed examples
        assert "Quick fix suggestions:" in formatted
        assert "WHY THIS MATTERS:" not in formatted
        assert "GOOD EXAMPLE" not in formatted
        assert "BAD EXAMPLE" not in formatted

    def test_format_explanation_contains_severity(self):
        """Test that formatted explanation includes severity."""
        issue = Issue(
            severity=Severity.INFO,
            file="test.py",
            function_name="func",
            start_line=5,
            end_line=40,
            rule_name="function-too-long",
            message="Function is somewhat long",
        )

        explanation = get_explanation(issue)
        formatted = format_explanation(issue, explanation, verbose=True)

        assert "Severity: INFO" in formatted

    def test_format_explanation_contains_location(self):
        """Test that formatted explanation includes file location."""
        issue = Issue(
            severity=Severity.CRITICAL,
            file="my_module.py",
            function_name="process_data",
            start_line=42,
            end_line=100,
            rule_name="function-too-long",
            message="Function is too long",
        )

        explanation = get_explanation(issue)
        formatted = format_explanation(issue, explanation, verbose=True)

        assert "my_module.py" in formatted
        assert "42-100" in formatted
        assert "process_data()" in formatted


class TestGetSeverityGuidance:
    """Test get_severity_guidance function."""

    def test_critical_severity_guidance(self):
        """Test guidance for CRITICAL severity."""
        guidance = get_severity_guidance(Severity.CRITICAL)

        assert "CRITICAL" in guidance
        assert "immediately" in guidance.lower()
        assert "fundamental" in guidance.lower()

    def test_warn_severity_guidance(self):
        """Test guidance for WARN severity."""
        guidance = get_severity_guidance(Severity.WARN)

        assert "WARNING" in guidance
        assert "moderate" in guidance.lower()

    def test_info_severity_guidance(self):
        """Test guidance for INFO severity."""
        guidance = get_severity_guidance(Severity.INFO)

        assert "INFO" in guidance
        assert "minor" in guidance.lower()


class TestExplanationContent:
    """Test that all explanation templates have required content."""

    def test_all_rules_have_explanations(self):
        """Test that explanations exist for all rules."""
        expected_rules = ["function-too-long", "too-many-parameters", "deep-nesting"]

        for rule in expected_rules:
            assert rule in EXPLANATIONS, f"Missing explanation for rule: {rule}"

    def test_all_explanations_have_required_fields(self):
        """Test that all explanations have required fields."""
        for rule_name, explanation in EXPLANATIONS.items():
            assert explanation.why_it_matters, f"{rule_name}: Missing why_it_matters"
            assert explanation.how_to_fix, f"{rule_name}: Missing how_to_fix"
            assert explanation.good_example, f"{rule_name}: Missing good_example"
            assert explanation.bad_example, f"{rule_name}: Missing bad_example"
            assert explanation.references, f"{rule_name}: Missing references"

            # Ensure how_to_fix has multiple steps
            assert (
                len(explanation.how_to_fix) >= 3
            ), f"{rule_name}: Should have at least 3 fix suggestions"

            # Ensure references are provided
            assert (
                len(explanation.references) >= 2
            ), f"{rule_name}: Should have at least 2 references"

    def test_examples_contain_code_markers(self):
        """Test that examples contain recognizable code markers."""
        for rule_name, explanation in EXPLANATIONS.items():
            # Good examples should contain "GOOD" or similar markers
            assert (
                "GOOD" in explanation.good_example or "def " in explanation.good_example
            ), f"{rule_name}: Good example should be clearly marked or contain code"

            # Bad examples should contain "BAD" or similar markers
            assert (
                "BAD" in explanation.bad_example or "def " in explanation.bad_example
            ), f"{rule_name}: Bad example should be clearly marked or contain code"

    def test_explanations_mention_key_concepts(self):
        """Test that explanations mention important concepts."""
        # function-too-long should mention SRP
        long_func_explanation = EXPLANATIONS["function-too-long"]
        assert (
            "Single Responsibility" in long_func_explanation.why_it_matters
            or "SRP" in long_func_explanation.why_it_matters
        )

        # too-many-parameters should mention configuration/dataclass
        many_params_explanation = EXPLANATIONS["too-many-parameters"]
        assert any(
            "dataclass" in step.lower() or "config" in step.lower()
            for step in many_params_explanation.how_to_fix
        )

        # deep-nesting should mention guard clauses
        deep_nesting_explanation = EXPLANATIONS["deep-nesting"]
        assert any(
            "guard" in step.lower() or "early return" in step.lower()
            for step in deep_nesting_explanation.how_to_fix
        )
