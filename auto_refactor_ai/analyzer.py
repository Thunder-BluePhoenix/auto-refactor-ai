import ast
from dataclasses import dataclass
from enum import Enum
from typing import List


class Severity(Enum):
    """Severity levels for code issues."""

    INFO = "INFO"
    WARN = "WARN"
    CRITICAL = "CRITICAL"


@dataclass
class Issue:
    """Represents a code quality issue found during analysis."""

    severity: Severity
    file: str
    function_name: str
    start_line: int
    end_line: int
    rule_name: str
    message: str
    details: dict = None  # Optional metadata about the issue

    def to_dict(self):
        """Convert issue to dictionary for JSON serialization."""
        return {
            "severity": self.severity.value,
            "file": self.file,
            "function_name": self.function_name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "rule_name": self.rule_name,
            "message": self.message,
            "details": self.details or {},
        }


class NestingVisitor(ast.NodeVisitor):
    """Visitor to calculate maximum nesting depth in a function."""

    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0

    def visit_If(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_For(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_With(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1


def check_function_length(node: ast.FunctionDef, path: str, max_length: int = 30) -> Issue:
    """Rule 1: Check if function is too long."""
    start = node.lineno
    end = getattr(node, "end_lineno", start)
    length = end - start + 1

    if length > max_length:
        # Determine severity based on how much it exceeds the limit
        if length > max_length * 2:
            severity = Severity.CRITICAL
        elif length > max_length * 1.5:
            severity = Severity.WARN
        else:
            severity = Severity.INFO

        message = (
            f"Function '{node.name}' is {length} lines long (max: {max_length}). "
            f"Consider splitting it into smaller functions with single responsibilities."
        )

        return Issue(
            severity=severity,
            file=path,
            function_name=node.name,
            start_line=start,
            end_line=end,
            rule_name="function-too-long",
            message=message,
            details={"length": length, "max_length": max_length},
        )
    return None


def check_too_many_parameters(node: ast.FunctionDef, path: str, max_params: int = 5) -> Issue:
    """Rule 2: Check if function has too many parameters."""
    start = node.lineno
    end = getattr(node, "end_lineno", start)

    # Count all parameters (args, kwargs, kwonly, etc.)
    param_count = (
        len(node.args.args)
        + len(node.args.kwonlyargs)
        + (1 if node.args.vararg else 0)
        + (1 if node.args.kwarg else 0)
    )

    if param_count > max_params:
        # Determine severity
        if param_count > max_params * 2:
            severity = Severity.CRITICAL
        elif param_count > max_params * 1.5:
            severity = Severity.WARN
        else:
            severity = Severity.INFO

        message = (
            f"Function '{node.name}' has {param_count} parameters (recommended: ≤ {max_params}). "
            f"Consider grouping related parameters into a dataclass or config object."
        )

        return Issue(
            severity=severity,
            file=path,
            function_name=node.name,
            start_line=start,
            end_line=end,
            rule_name="too-many-parameters",
            message=message,
            details={"param_count": param_count, "max_params": max_params},
        )
    return None


def check_deep_nesting(node: ast.FunctionDef, path: str, max_depth: int = 3) -> Issue:
    """Rule 3: Check if function has too much nesting."""
    start = node.lineno
    end = getattr(node, "end_lineno", start)

    # Calculate nesting depth
    visitor = NestingVisitor()
    visitor.visit(node)
    depth = visitor.max_depth

    if depth > max_depth:
        # Determine severity
        if depth > max_depth * 2:
            severity = Severity.CRITICAL
        elif depth > max_depth * 1.5:
            severity = Severity.WARN
        else:
            severity = Severity.INFO

        message = (
            f"Function '{node.name}' has {depth} levels of nesting (max: {max_depth}). "
            f"High nesting makes code harder to understand. Consider extracting nested logic into helper functions."
        )

        return Issue(
            severity=severity,
            file=path,
            function_name=node.name,
            start_line=start,
            end_line=end,
            rule_name="deep-nesting",
            message=message,
            details={"nesting_depth": depth, "max_depth": max_depth},
        )
    return None


def analyze_file(
    path: str, max_function_length: int = 30, max_parameters: int = 5, max_nesting_depth: int = 3
) -> List[Issue]:
    """
    Analyze a Python file and return a list of code quality issues.

    Args:
        path: Path to the Python file to analyze
        max_function_length: Maximum allowed function length in lines
        max_parameters: Maximum allowed number of parameters
        max_nesting_depth: Maximum allowed nesting depth

    Returns:
        List of Issue objects found in the file
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"[ERROR] Cannot read {path}: {e}")
        return []

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as e:
        print(f"[ERROR] Cannot parse {path}: {e}")
        return []

    issues: List[Issue] = []

    # Apply all rules to each function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Rule 1: Function length
            issue = check_function_length(node, path, max_function_length)
            if issue:
                issues.append(issue)

            # Rule 2: Too many parameters
            issue = check_too_many_parameters(node, path, max_parameters)
            if issue:
                issues.append(issue)

            # Rule 3: Deep nesting
            issue = check_deep_nesting(node, path, max_nesting_depth)
            if issue:
                issues.append(issue)

    return issues
