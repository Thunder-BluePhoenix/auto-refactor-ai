"""Tests for analyzer module."""

import ast
import tempfile
from pathlib import Path

from auto_refactor_ai.analyzer import (
    Issue,
    NestingVisitor,
    Severity,
    analyze_file,
    check_deep_nesting,
    check_function_length,
    check_too_many_parameters,
)


class TestSeverity:
    """Test Severity enum."""

    def test_severity_values(self):
        """Test that severity levels have correct values."""
        assert Severity.INFO.value == "INFO"
        assert Severity.WARN.value == "WARN"
        assert Severity.CRITICAL.value == "CRITICAL"


class TestIssue:
    """Test Issue dataclass."""

    def test_issue_creation(self):
        """Test creating an Issue."""
        issue = Issue(
            severity=Severity.INFO,
            file="test.py",
            function_name="test_func",
            start_line=1,
            end_line=10,
            rule_name="test-rule",
            message="Test message",
            details={"key": "value"},
        )
        assert issue.severity == Severity.INFO
        assert issue.file == "test.py"
        assert issue.function_name == "test_func"
        assert issue.details == {"key": "value"}

    def test_issue_to_dict(self):
        """Test Issue.to_dict() method."""
        issue = Issue(
            severity=Severity.WARN,
            file="test.py",
            function_name="func",
            start_line=1,
            end_line=5,
            rule_name="rule",
            message="msg",
        )
        result = issue.to_dict()
        assert result["severity"] == "WARN"
        assert result["file"] == "test.py"
        assert result["function_name"] == "func"
        assert result["details"] == {}


class TestNestingVisitor:
    """Test NestingVisitor class."""

    def test_no_nesting(self):
        """Test function with no nesting."""
        code = """
def simple():
    x = 1
    return x
"""
        tree = ast.parse(code)
        func = tree.body[0]
        visitor = NestingVisitor()
        visitor.visit(func)
        assert visitor.max_depth == 0

    def test_single_if(self):
        """Test function with single if statement."""
        code = """
def single_if():
    if True:
        x = 1
"""
        tree = ast.parse(code)
        func = tree.body[0]
        visitor = NestingVisitor()
        visitor.visit(func)
        assert visitor.max_depth == 1

    def test_nested_loops(self):
        """Test nested for loops."""
        code = """
def nested():
    for i in range(10):
        for j in range(10):
            for k in range(10):
                x = i + j + k
"""
        tree = ast.parse(code)
        func = tree.body[0]
        visitor = NestingVisitor()
        visitor.visit(func)
        assert visitor.max_depth == 3

    def test_mixed_nesting(self):
        """Test mixed control structures."""
        code = """
def mixed():
    if True:
        for i in range(10):
            while i > 0:
                i -= 1
"""
        tree = ast.parse(code)
        func = tree.body[0]
        visitor = NestingVisitor()
        visitor.visit(func)
        assert visitor.max_depth == 3

    def test_with_statement(self):
        """Test with statement nesting."""
        code = """
def with_stmt():
    with open('file') as f:
        for line in f:
            x = line
"""
        tree = ast.parse(code)
        func = tree.body[0]
        visitor = NestingVisitor()
        visitor.visit(func)
        assert visitor.max_depth == 2


class TestCheckFunctionLength:
    """Test check_function_length rule."""

    def test_short_function(self):
        """Test that short functions pass."""
        code = """
def short():
    return 1
"""
        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_function_length(func, "test.py", max_length=30)
        assert issue is None

    def test_function_at_limit(self):
        """Test function exactly at the limit."""
        # Create a function with exactly 30 lines
        lines = ["def at_limit():\n"]
        for i in range(28):
            lines.append(f"    x{i} = {i}\n")
        lines.append("    return x0\n")
        code = "".join(lines)

        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_function_length(func, "test.py", max_length=30)
        assert issue is None

    def test_function_over_limit_info(self):
        """Test function slightly over limit (INFO)."""
        # 35 lines = 1.17x over 30 = INFO
        lines = ["def over_limit():\n"]
        for i in range(33):
            lines.append(f"    x{i} = {i}\n")
        lines.append("    return x0\n")
        code = "".join(lines)

        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_function_length(func, "test.py", max_length=30)
        assert issue is not None
        assert issue.severity == Severity.INFO
        assert issue.rule_name == "function-too-long"
        assert "over_limit" in issue.message

    def test_function_over_limit_warn(self):
        """Test function significantly over limit (WARN)."""
        # 50 lines = 1.67x over 30 = WARN
        lines = ["def very_long():\n"]
        for i in range(48):
            lines.append(f"    x{i} = {i}\n")
        lines.append("    return x0\n")
        code = "".join(lines)

        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_function_length(func, "test.py", max_length=30)
        assert issue is not None
        assert issue.severity == Severity.WARN

    def test_function_over_limit_critical(self):
        """Test function way over limit (CRITICAL)."""
        # 70 lines = 2.33x over 30 = CRITICAL
        lines = ["def extremely_long():\n"]
        for i in range(68):
            lines.append(f"    x{i} = {i}\n")
        lines.append("    return x0\n")
        code = "".join(lines)

        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_function_length(func, "test.py", max_length=30)
        assert issue is not None
        assert issue.severity == Severity.CRITICAL


class TestCheckTooManyParameters:
    """Test check_too_many_parameters rule."""

    def test_few_parameters(self):
        """Test function with few parameters."""
        code = "def func(a, b): pass"
        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_too_many_parameters(func, "test.py", max_params=5)
        assert issue is None

    def test_exactly_at_limit(self):
        """Test function exactly at parameter limit."""
        code = "def func(a, b, c, d, e): pass"
        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_too_many_parameters(func, "test.py", max_params=5)
        assert issue is None

    def test_over_limit_info(self):
        """Test function slightly over parameter limit (INFO)."""
        code = "def func(a, b, c, d, e, f): pass"
        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_too_many_parameters(func, "test.py", max_params=5)
        assert issue is not None
        assert issue.severity == Severity.INFO
        assert issue.rule_name == "too-many-parameters"

    def test_with_args_kwargs(self):
        """Test counting *args and **kwargs."""
        code = "def func(a, b, *args, **kwargs): pass"
        tree = ast.parse(code)
        func = tree.body[0]
        # Total: 2 regular + 1 *args + 1 **kwargs = 4
        issue = check_too_many_parameters(func, "test.py", max_params=3)
        assert issue is not None
        assert issue.details["param_count"] == 4

    def test_keyword_only_params(self):
        """Test keyword-only parameters."""
        code = "def func(a, b, *, c, d): pass"
        tree = ast.parse(code)
        func = tree.body[0]
        # Total: 2 regular + 2 kwonly = 4
        issue = check_too_many_parameters(func, "test.py", max_params=3)
        assert issue is not None
        assert issue.details["param_count"] == 4


class TestCheckDeepNesting:
    """Test check_deep_nesting rule."""

    def test_no_nesting(self):
        """Test function with no nesting."""
        code = """
def simple():
    x = 1
    return x
"""
        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_deep_nesting(func, "test.py", max_depth=3)
        assert issue is None

    def test_at_limit(self):
        """Test function exactly at nesting limit."""
        code = """
def at_limit():
    if True:
        if True:
            if True:
                x = 1
"""
        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_deep_nesting(func, "test.py", max_depth=3)
        assert issue is None

    def test_over_limit_info(self):
        """Test function slightly over nesting limit (INFO)."""
        code = """
def over_limit():
    if True:
        if True:
            if True:
                if True:
                    x = 1
"""
        tree = ast.parse(code)
        func = tree.body[0]
        issue = check_deep_nesting(func, "test.py", max_depth=3)
        assert issue is not None
        assert issue.severity == Severity.INFO
        assert issue.rule_name == "deep-nesting"


class TestAnalyzeFile:
    """Test analyze_file function."""

    def test_analyze_good_file(self):
        """Test analyzing a file with no issues."""
        code = """
def good_function(x, y):
    '''A good function.'''
    return x + y
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            issues = analyze_file(temp_path)
            assert len(issues) == 0
        finally:
            Path(temp_path).unlink()

    def test_analyze_file_with_issues(self):
        """Test analyzing a file with multiple issues."""
        code = """
def bad_function(a, b, c, d, e, f, g):
    '''Has too many parameters.'''
    result = []
    for i in range(10):
        if i > 0:
            for j in range(10):
                if j > 0:
                    for k in range(10):
                        result.append(i + j + k)
    return result
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            issues = analyze_file(temp_path, max_parameters=5, max_nesting_depth=3)
            # Should find: too many params (7 > 5) and deep nesting (5 > 3)
            assert len(issues) >= 2
            rule_names = {issue.rule_name for issue in issues}
            assert "too-many-parameters" in rule_names
            assert "deep-nesting" in rule_names
        finally:
            Path(temp_path).unlink()

    def test_analyze_nonexistent_file(self):
        """Test analyzing a non-existent file."""
        issues = analyze_file("nonexistent_file.py")
        assert len(issues) == 0

    def test_analyze_invalid_syntax(self):
        """Test analyzing a file with syntax errors."""
        code = "def bad syntax here"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            issues = analyze_file(temp_path)
            # Should handle syntax error gracefully
            assert len(issues) == 0
        finally:
            Path(temp_path).unlink()

    def test_analyze_with_custom_thresholds(self):
        """Test analyzing with custom thresholds."""
        code = """
def func(a, b, c, d):
    '''Has 4 parameters, 15 lines.'''
    x1 = 1
    x2 = 2
    x3 = 3
    x4 = 4
    x5 = 5
    x6 = 6
    x7 = 7
    x8 = 8
    x9 = 9
    return x1 + x2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            # Should trigger with strict thresholds
            issues = analyze_file(
                temp_path, max_function_length=10, max_parameters=3, max_nesting_depth=2
            )
            assert len(issues) >= 2  # Length and params
        finally:
            Path(temp_path).unlink()
