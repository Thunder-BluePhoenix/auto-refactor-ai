import argparse
from pathlib import Path

from .analyzer import analyze_file


def main():
    parser = argparse.ArgumentParser(
        description="Auto Refactor AI – basic static analyzer (V0)"
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyze",
    )
    parser.add_argument(
        "--max-len",
        type=int,
        default=30,
        help="Maximum allowed function length (in lines). Default: 30",
    )

    args = parser.parse_args()
    target_path = Path(args.path)

    if target_path.is_file():
        analyze_single_file(target_path, args.max_len)
    elif target_path.is_dir():
        analyze_directory(target_path, args.max_len)
    else:
        print(f"[ERROR] Path not found: {target_path}")


def analyze_single_file(path: Path, max_len: int):
    issues = analyze_file(str(path), max_function_length=max_len)
    print_issues(issues)


def analyze_directory(root: Path, max_len: int):
    python_files = list(root.rglob("*.py"))
    if not python_files:
        print("[INFO] No Python files found.")
        return

    for file in python_files:
        issues = analyze_file(str(file), max_function_length=max_len)
        print_issues(issues)


def print_issues(issues):
    if not issues:
        return

    for issue in issues:
        print(
            f"\n[LONG FUNCTION] {issue.file}:{issue.start_line}-{issue.end_line}\n"
            f"  - Function : {issue.function_name}\n"
            f"  - Length   : {issue.length} lines\n"
            f"  - Suggestion: {issue.message}\n"
        )


if __name__ == "__main__":
    main()
