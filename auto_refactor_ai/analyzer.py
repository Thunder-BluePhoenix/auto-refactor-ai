import ast
from dataclasses import dataclass
from typing import List


@dataclass
class FunctionIssue:
    file: str
    function_name: str
    start_line: int
    end_line: int
    length: int
    message: str


def analyze_file(path: str, max_function_length: int = 30) -> List[FunctionIssue]:
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as e:
        print(f"[ERROR] Cannot parse {path}: {e}")
        return []

    issues: List[FunctionIssue] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            # end_lineno exists in 3.8+, fallback just in case
            end = getattr(node, "end_lineno", start)
            length = end - start + 1

            if length > max_function_length:
                message = (
                    f"Function '{node.name}' in {path} is {length} lines long. "
                    f"Consider splitting it into smaller functions with single responsibilities."
                )
                issues.append(
                    FunctionIssue(
                        file=path,
                        function_name=node.name,
                        start_line=start,
                        end_line=end,
                        length=length,
                        message=message,
                    )
                )

    return issues
