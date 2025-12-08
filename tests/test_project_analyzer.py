"""Tests for project_analyzer module (V8)."""

import ast
import tempfile
from pathlib import Path

from auto_refactor_ai.project_analyzer import (
    DuplicateGroup,
    FunctionSignature,
    ProjectAnalysis,
    analyze_project,
    extract_functions_from_file,
    find_duplicates,
    format_project_analysis,
    hash_function_body,
    normalize_ast,
)


class TestASTNormalizer:
    """Test AST normalization."""

    def test_normalize_variable_names(self):
        """Test that variable names are normalized."""
        code = """
def foo():
    x = 1
    y = 2
    return x + y
"""
        tree = ast.parse(code)
        func = tree.body[0]
        normalized = normalize_ast(func)

        # Should not contain original variable names
        assert "var_" in normalized or "x" not in normalized

    def test_same_structure_same_hash(self):
        """Test functions with same structure have same hash."""
        code1 = """
def foo(a, b):
    result = a + b
    return result
"""
        code2 = """
def bar(x, y):
    output = x + y
    return output
"""
        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        hash1 = hash_function_body(tree1.body[0])
        hash2 = hash_function_body(tree2.body[0])

        assert hash1 == hash2

    def test_different_structure_different_hash(self):
        """Test functions with different structure have different hash."""
        code1 = """
def foo(a, b):
    return a + b
"""
        code2 = """
def bar(a, b):
    return a * b
"""
        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        hash1 = hash_function_body(tree1.body[0])
        hash2 = hash_function_body(tree2.body[0])

        assert hash1 != hash2


class TestExtractFunctions:
    """Test function extraction."""

    def test_extract_from_file(self):
        """Test extracting functions from a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def foo():
    pass

def bar(x, y):
    return x + y
"""
            )
            f.flush()

            functions = extract_functions_from_file(f.name)

            assert len(functions) == 2
            assert functions[0].name == "foo"
            assert functions[1].name == "bar"
            assert functions[1].parameter_count == 2

    def test_extract_handles_syntax_error(self):
        """Test that syntax errors are handled gracefully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def broken(:\n    pass")
            f.flush()

            functions = extract_functions_from_file(f.name)

            # Should return empty list, not crash
            assert functions == []


class TestFindDuplicates:
    """Test duplicate detection."""

    def test_find_exact_duplicates(self):
        """Test finding exact duplicate functions."""
        # Create functions with same hash
        functions = [
            FunctionSignature(
                file="a.py",
                name="foo",
                start_line=1,
                end_line=10,
                parameters=["x"],
                body_hash="abc123",
                parameter_count=1,
                line_count=10,
            ),
            FunctionSignature(
                file="b.py",
                name="bar",
                start_line=1,
                end_line=10,
                parameters=["y"],
                body_hash="abc123",  # Same hash
                parameter_count=1,
                line_count=10,
            ),
        ]

        duplicates = find_duplicates(functions, min_lines=5)

        assert len(duplicates) == 1
        assert duplicates[0].count == 2

    def test_no_duplicates(self):
        """Test when there are no duplicates."""
        functions = [
            FunctionSignature(
                file="a.py",
                name="foo",
                start_line=1,
                end_line=10,
                parameters=["x"],
                body_hash="abc123",
                parameter_count=1,
                line_count=10,
            ),
            FunctionSignature(
                file="b.py",
                name="bar",
                start_line=1,
                end_line=10,
                parameters=["y"],
                body_hash="def456",  # Different hash
                parameter_count=1,
                line_count=10,
            ),
        ]

        duplicates = find_duplicates(functions, min_lines=5)

        assert len(duplicates) == 0

    def test_filter_by_min_lines(self):
        """Test that short functions are filtered out."""
        functions = [
            FunctionSignature(
                file="a.py",
                name="foo",
                start_line=1,
                end_line=3,
                parameters=[],
                body_hash="abc123",
                parameter_count=0,
                line_count=3,  # Too short
            ),
            FunctionSignature(
                file="b.py",
                name="bar",
                start_line=1,
                end_line=3,
                parameters=[],
                body_hash="abc123",
                parameter_count=0,
                line_count=3,  # Too short
            ),
        ]

        duplicates = find_duplicates(functions, min_lines=5)

        assert len(duplicates) == 0

    def test_suggest_module_mixed_dirs(self):
        """Test suggesting module when functions are in different directories."""
        from auto_refactor_ai.project_analyzer import _suggest_module

        functions = [
            FunctionSignature(
                file="dir1/a.py",
                name="f1",
                start_line=1,
                end_line=10,
                parameters=[],
                body_hash="abc",
                parameter_count=0,
                line_count=10,
            ),
            FunctionSignature(
                file="dir2/b.py",
                name="f2",
                start_line=1,
                end_line=10,
                parameters=[],
                body_hash="abc",
                parameter_count=0,
                line_count=10,
            ),
        ]

        module = _suggest_module(functions)
        assert module.endswith("shared.py")

    def test_find_common_words_no_common(self):
        """Test finding common words when there are none."""
        from auto_refactor_ai.project_analyzer import _find_common_words

        words = _find_common_words(["create_user", "delete_post"])
        assert words == []

    def test_find_common_words_empty(self):
        """Test finding common words with empty list."""
        from auto_refactor_ai.project_analyzer import _find_common_words

        assert _find_common_words([]) == []


class TestDuplicateGroup:
    """Test DuplicateGroup properties."""

    def test_potential_savings(self):
        """Test potential savings calculation."""
        functions = [
            FunctionSignature(
                file="a.py",
                name="f1",
                start_line=1,
                end_line=10,
                parameters=[],
                body_hash="abc",
                parameter_count=0,
                line_count=10,
            ),
            FunctionSignature(
                file="b.py",
                name="f2",
                start_line=1,
                end_line=10,
                parameters=[],
                body_hash="abc",
                parameter_count=0,
                line_count=10,
            ),
            FunctionSignature(
                file="c.py",
                name="f3",
                start_line=1,
                end_line=10,
                parameters=[],
                body_hash="abc",
                parameter_count=0,
                line_count=10,
            ),
        ]

        group = DuplicateGroup(functions=functions, similarity=1.0)

        # 3 functions * 10 lines = 30 total
        # Could be consolidated to ~10 lines
        # Savings = 30 - 10 = 20
        assert group.potential_savings == 20


class TestProjectAnalysis:
    """Test project-level analysis."""

    def test_analyze_directory(self):
        """Test analyzing a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "a.py").write_text(
                """
def helper(x):
    result = x * 2
    return result
"""
            )
            Path(tmpdir, "b.py").write_text(
                """
def processor(y):
    result = y * 2
    return result
"""
            )

            analysis = analyze_project(tmpdir, min_lines=3)

            assert analysis.files_analyzed == 2
            assert analysis.functions_found == 2

    def test_analyze_single_file(self):
        """Test analyzing a single file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def foo():
    pass

def bar():
    pass
"""
            )
            f.flush()

            analysis = analyze_project(f.name)

            assert analysis.files_analyzed == 1
            assert analysis.functions_found == 2


class TestFormatProjectAnalysis:
    """Test formatting functions."""

    def test_format_with_duplicates(self):
        """Test formatting analysis with duplicates."""
        group = DuplicateGroup(
            functions=[
                FunctionSignature(
                    file="a.py",
                    name="foo",
                    start_line=1,
                    end_line=10,
                    parameters=[],
                    body_hash="abc",
                    parameter_count=0,
                    line_count=10,
                ),
                FunctionSignature(
                    file="b.py",
                    name="bar",
                    start_line=1,
                    end_line=10,
                    parameters=[],
                    body_hash="abc",
                    parameter_count=0,
                    line_count=10,
                ),
            ],
            similarity=1.0,
            suggested_name="helper",
            suggested_module="utils.py",
        )

        analysis = ProjectAnalysis(
            root_path="/test",
            files_analyzed=2,
            functions_found=10,
            duplicates=[group],
        )

        output = format_project_analysis(analysis)

        assert "DUPLICATE CODE DETECTED" in output
        assert "foo()" in output
        assert "bar()" in output

    def test_format_no_duplicates(self):
        """Test formatting analysis without duplicates."""
        analysis = ProjectAnalysis(
            root_path="/test",
            files_analyzed=5,
            functions_found=20,
            duplicates=[],
        )

        output = format_project_analysis(analysis)

        assert "No duplicate code detected" in output


class TestFunctionSignature:
    """Test FunctionSignature dataclass."""

    def test_location_property(self):
        """Test location string property."""
        sig = FunctionSignature(
            file="test.py",
            name="foo",
            start_line=10,
            end_line=20,
            parameters=["a", "b"],
            body_hash="abc",
            parameter_count=2,
            line_count=11,
        )

        assert sig.location == "test.py:10-20"

    def test_qualified_name_property(self):
        """Test qualified name property."""
        sig = FunctionSignature(
            file="path/to/module.py",
            name="foo",
            start_line=1,
            end_line=5,
            parameters=[],
            body_hash="abc",
            parameter_count=0,
            line_count=5,
        )

        assert sig.qualified_name == "module.foo"
