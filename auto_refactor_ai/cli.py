import argparse
import json
import sys
from pathlib import Path

from .analyzer import analyze_file, Severity
from .config import load_config, Config


def main():
    parser = argparse.ArgumentParser(
        description="Auto Refactor AI – Static analyzer for Python code quality (V2)"
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyze",
    )
    parser.add_argument(
        "--max-len",
        type=int,
        default=None,
        help="Maximum allowed function length (in lines). Overrides config file.",
    )
    parser.add_argument(
        "--max-params",
        type=int,
        default=None,
        help="Maximum allowed parameters per function. Overrides config file.",
    )
    parser.add_argument(
        "--max-nesting",
        type=int,
        default=None,
        help="Maximum allowed nesting depth. Overrides config file.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config file (.toml or .yaml). Auto-discovered if not specified.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format: 'text' (human-readable) or 'json' (machine-readable). Default: text",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(Path(args.config) if args.config else None)

    # Command-line arguments override config file
    if args.max_len is not None:
        config.max_function_length = args.max_len
    if args.max_params is not None:
        config.max_parameters = args.max_params
    if args.max_nesting is not None:
        config.max_nesting_depth = args.max_nesting

    target_path = Path(args.path)

    if target_path.is_file():
        issues = analyze_single_file(target_path, config)
    elif target_path.is_dir():
        issues = analyze_directory(target_path, config)
    else:
        print(f"[ERROR] Path not found: {target_path}")
        sys.exit(1)

    # Output results
    if args.format == "json":
        print_json(issues, config)
    else:
        print_issues(issues)
        if target_path.is_dir():
            print_summary(issues)


def analyze_single_file(path: Path, config: Config):
    """Analyze a single file and return issues."""
    issues = analyze_file(
        str(path),
        max_function_length=config.max_function_length,
        max_parameters=config.max_parameters,
        max_nesting_depth=config.max_nesting_depth
    )
    return issues


def analyze_directory(root: Path, config: Config):
    """Analyze all Python files in a directory and return all issues."""
    python_files = list(root.rglob("*.py"))
    if not python_files:
        print("[INFO] No Python files found.")
        return []

    all_issues = []
    for file in python_files:
        issues = analyze_file(
            str(file),
            max_function_length=config.max_function_length,
            max_parameters=config.max_parameters,
            max_nesting_depth=config.max_nesting_depth
        )
        all_issues.extend(issues)

    return all_issues


def print_issues(issues):
    """Print issues in human-readable text format."""
    if not issues:
        print("\n✓ No issues found! Your code looks good.\n")
        return

    # Sort by severity (CRITICAL > WARN > INFO) then by file
    severity_order = {Severity.CRITICAL: 0, Severity.WARN: 1, Severity.INFO: 2}
    sorted_issues = sorted(
        issues,
        key=lambda x: (severity_order[x.severity], x.file, x.start_line)
    )

    for issue in sorted_issues:
        severity_label = f"[{issue.severity.value}]"
        print(
            f"\n{severity_label} {issue.file}:{issue.start_line}-{issue.end_line}  {issue.function_name}()"
        )
        print(f"  - {issue.message}")


def print_summary(issues):
    """Print a summary of issues by severity."""
    if not issues:
        return

    critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
    warn_count = sum(1 for i in issues if i.severity == Severity.WARN)
    info_count = sum(1 for i in issues if i.severity == Severity.INFO)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  CRITICAL: {critical_count}")
    print(f"  WARN:     {warn_count}")
    print(f"  INFO:     {info_count}")
    print(f"  TOTAL:    {len(issues)}")
    print("=" * 60 + "\n")


def print_json(issues, config: Config):
    """Print issues in JSON format."""
    output = {
        "config": config.to_dict(),
        "summary": {
            "total": len(issues),
            "critical": sum(1 for i in issues if i.severity == Severity.CRITICAL),
            "warn": sum(1 for i in issues if i.severity == Severity.WARN),
            "info": sum(1 for i in issues if i.severity == Severity.INFO),
        },
        "issues": [issue.to_dict() for issue in issues]
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
