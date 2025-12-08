import argparse
import json
import sys
from pathlib import Path

from .analyzer import Severity, analyze_file
from .config import Config, load_config
from .explanations import format_explanation, get_explanation, get_severity_guidance


def create_argument_parser():
    """Create and configure the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Auto Refactor AI – Static analyzer with AI suggestions, auto-apply, project analysis, and git support (V9)"
    )
    parser.add_argument("path", nargs="?", default=".", help="Python file or directory to analyze")
    parser.add_argument(
        "--max-len", type=int, default=None, help="Maximum allowed function length."
    )
    parser.add_argument("--max-params", type=int, default=None, help="Maximum allowed parameters.")
    parser.add_argument(
        "--max-nesting", type=int, default=None, help="Maximum allowed nesting depth."
    )
    parser.add_argument("--config", type=str, default=None, help="Path to config file.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format. Default: text",
    )
    parser.add_argument("--explain", action="store_true", help="Show detailed explanations (V5)")
    parser.add_argument(
        "--explain-summary", action="store_true", help="Show brief explanations (V5)"
    )
    # V6: AI Suggestions
    parser.add_argument(
        "--ai-suggestions", action="store_true", help="Get AI-powered suggestions (V6)"
    )
    parser.add_argument(
        "--ai-provider",
        choices=["openai", "anthropic", "google", "ollama"],
        default=None,
        help="LLM provider to use.",
    )
    parser.add_argument("--ai-model", type=str, default=None, help="Specific model.")
    parser.add_argument(
        "--ai-max-issues", type=int, default=5, help="Max issues for AI suggestions."
    )
    parser.add_argument(
        "--check-providers", action="store_true", help="Check available LLM providers."
    )
    # V7: Auto-Refactor Mode
    parser.add_argument("--apply", action="store_true", help="Apply refactorings (V7)")
    parser.add_argument("--dry-run", action="store_true", help="Show without applying")
    parser.add_argument("--interactive", action="store_true", help="Ask before each change")
    parser.add_argument("--backup", action="store_true", default=True, help="Create backups")
    parser.add_argument("--no-backup", action="store_true", help="Disable backups")
    parser.add_argument(
        "--backup-dir", type=str, default=".auto-refactor-backup", help="Backup directory"
    )
    # V8: Project-Level Analysis
    parser.add_argument("--project", "-p", action="store_true", help="Project-level analysis (V8)")
    parser.add_argument("--find-duplicates", action="store_true", help="Find duplicate code (V8)")
    parser.add_argument(
        "--similarity-threshold", type=float, default=0.8, help="Duplicate threshold"
    )
    parser.add_argument("--min-lines", type=int, default=5, help="Minimum lines for duplicates")
    # V9: Git Integration
    parser.add_argument("--git", action="store_true", help="Analyze modified files (V9)")
    parser.add_argument("--staged", action="store_true", help="Analyze staged files (V9)")
    # V10: Refactor Planning
    parser.add_argument("--plan", action="store_true", help="Generate a refactoring plan (V10)")
    parser.add_argument(
        "--plan-format",
        choices=["text", "markdown", "html"],
        default="text",
        help="Format for the refactoring plan",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None, help="Output file for saving reports"
    )
    return parser


def apply_config_overrides(config, args):
    """Apply command-line overrides to config."""
    if args.max_len is not None:
        config.max_function_length = args.max_len
    if args.max_params is not None:
        config.max_parameters = args.max_params
    if args.max_nesting is not None:
        config.max_nesting_depth = args.max_nesting
    return config


def collect_files_to_analyze(args, config):
    """Collect files to analyze based on args (git, directory, or single file)."""
    target_path = Path(args.path)

    if args.git or args.staged:
        from .git_utils import get_changed_files, is_git_repo

        target_path_str = str(target_path.resolve())
        if not is_git_repo(target_path_str):
            print(f"Error: {target_path_str} is not in a git repository.")
            sys.exit(1)

        git_files = get_changed_files(target_path_str, staged=args.staged)
        if not git_files:
            mode = "staged" if args.staged else "modified"
            print(f"No {mode} Python files found in git repository.")
            sys.exit(0)

        print(f"Analyzing {len(git_files)} {'staged' if args.staged else 'modified'} file(s)...")
        return git_files, target_path

    if target_path.is_file():
        return [str(target_path)], target_path
    elif target_path.is_dir():
        return [str(f) for f in target_path.rglob("*.py")], target_path
    else:
        print(f"[ERROR] Path not found: {args.path}")
        sys.exit(1)


def run_analysis(files, config):
    """Run analysis on collected files."""
    issues = []
    for file_path in files:
        file_issues = analyze_file(
            file_path,
            max_function_length=config.max_function_length,
            max_parameters=config.max_parameters,
            max_nesting_depth=config.max_nesting_depth,
        )
        issues.extend(file_issues)
    return issues


def output_results(issues, args, config, target_path):
    """Output analysis results in the requested format."""
    if args.format == "json":
        print_json(issues, config)
    else:
        if args.explain or args.explain_summary:
            print_issues_with_explanations(
                issues, verbose=args.explain, summary=args.explain_summary
            )
        else:
            print_issues(issues)

        if target_path.is_dir():
            print_summary(issues)


def main():
    """Main entry point for the CLI."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Check providers and exit if requested
    if args.check_providers:
        from .ai_suggestions import get_provider_status_message

        print(get_provider_status_message())
        sys.exit(0)

    # V8: Project-level analysis mode
    if (args.project or args.find_duplicates) and not args.plan:
        handle_project_analysis(args)
        return

    # Load and configure
    config = load_config(Path(args.config) if args.config else None)
    config = apply_config_overrides(config, args)

    # Collect files and run analysis
    files, target_path = collect_files_to_analyze(args, config)
    issues = run_analysis(files, config)

    # V10: Refactor Planning Mode
    if args.plan:
        handle_refactor_plan(args, config, issues)
        return

    # V6: AI Suggestions mode
    if args.ai_suggestions:
        handle_ai_suggestions(issues, args)
        return

    # Output results
    output_results(issues, args, config, target_path)


def handle_ai_suggestions(issues, args):
    """Handle AI suggestions mode (V6) with optional auto-apply (V7)."""
    from .ai_suggestions import (
        get_ai_suggestions,
        print_ai_suggestions,
    )
    from .llm_providers import LLMConfig, LLMProvider

    if not issues:
        print("\n✓ No issues found! Your code looks good - no AI suggestions needed.\n")
        return

    # Build LLM config from args
    llm_config = None
    if args.ai_provider or args.ai_model:
        provider = LLMProvider(args.ai_provider) if args.ai_provider else LLMProvider.OPENAI
        llm_config = LLMConfig.from_env(provider)
        if args.ai_model:
            llm_config.model = args.ai_model

    print("\n🤖 Generating AI refactoring suggestions...")
    print(f"   Analyzing up to {args.ai_max_issues} issues...\n")

    # Get AI suggestions
    summary = get_ai_suggestions(
        issues=issues,
        config=llm_config,
        max_issues=args.ai_max_issues,
        skip_info=True,
    )

    # V7: Auto-apply mode
    if args.apply:
        handle_auto_refactor(summary, args)
        return

    # V6: Just print suggestions
    print_ai_suggestions(summary, show_original=True)


def handle_project_analysis(args):
    """Handle project-level analysis mode (V8)."""
    from .project_analyzer import analyze_project, print_project_analysis

    target_path = Path(args.path)

    if not target_path.exists():
        print(f"[ERROR] Path not found: {target_path}")
        return

    print(f"\n🔍 Analyzing project: {target_path}")
    print(f"   Similarity threshold: {args.similarity_threshold}")
    print(f"   Minimum lines: {args.min_lines}\n")

    analysis = analyze_project(
        root_path=str(target_path),
        min_lines=args.min_lines,
        similarity_threshold=args.similarity_threshold,
    )

    print_project_analysis(analysis)


def handle_refactor_plan(args, config, issues):
    """Handle refactor planning mode (V10)."""
    from .llm_providers import LLMConfig, LLMProvider
    from .project_analyzer import analyze_project
    from .refactor_planner import RefactorPlanner

    # Run project analysis for duplicates if it's a directory
    project_analysis = None
    target_path = Path(args.path)
    if target_path.is_dir():
        print("🔍 Analyzed project structure for duplicates...")
        project_analysis = analyze_project(
            root_path=str(target_path),
            min_lines=args.min_lines,
            similarity_threshold=args.similarity_threshold,
        )

    # Build LLM config if AI suggestions requested
    llm_config = None
    include_llm = args.ai_suggestions
    if include_llm:
        if args.ai_provider or args.ai_model:
            provider = LLMProvider(args.ai_provider) if args.ai_provider else LLMProvider.OPENAI
            llm_config = LLMConfig.from_env(provider)
            if args.ai_model:
                llm_config.model = args.ai_model
        print("🤖 Generating AI strategic advice...")

    # Initialize planner and generate plan
    print("🧠 Generating strategic refactoring plan...")
    planner = RefactorPlanner(issues, project_analysis)
    plan = planner.generate_plan(include_llm_advice=include_llm, llm_config=llm_config)

    # Format the output
    output = planner.format_plan(plan, format_type=args.plan_format)

    # Save to file or print
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output, encoding="utf-8")
        print(f"\n📄 Report saved to: {output_path}")
    else:
        print(output)


def handle_auto_refactor(ai_summary, args):
    """Handle auto-refactor mode (V7)."""
    from .auto_refactor import auto_refactor, print_refactor_results

    if not ai_summary.results:
        if ai_summary.errors:
            print("\n⚠️  Errors occurred during AI analysis:")
            for error in ai_summary.errors:
                print(f"   • {error}")
        else:
            print("\n✓ No suggestions to apply.\n")
        return

    # Determine mode
    dry_run = args.dry_run
    interactive = args.interactive
    create_backups = args.backup and not args.no_backup
    backup_dir = args.backup_dir

    # Show mode info
    mode_info = []
    if dry_run:
        mode_info.append("DRY RUN")
    if interactive:
        mode_info.append("INTERACTIVE")
    if not create_backups:
        mode_info.append("NO BACKUP")

    mode_str = f" ({', '.join(mode_info)})" if mode_info else ""
    print(f"\n🔧 Auto-Refactor Mode{mode_str}")
    print(f"   {len(ai_summary.results)} suggestion(s) to process\n")

    # Run auto-refactor
    result_summary = auto_refactor(
        ai_summary=ai_summary,
        dry_run=dry_run,
        interactive=interactive,
        backup_dir=backup_dir,
        create_backups=create_backups,
    )

    # Print results
    print_refactor_results(result_summary)


def analyze_single_file(path: Path, config: Config):
    """Analyze a single file and return issues."""
    issues = analyze_file(
        str(path),
        max_function_length=config.max_function_length,
        max_parameters=config.max_parameters,
        max_nesting_depth=config.max_nesting_depth,
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
            max_nesting_depth=config.max_nesting_depth,
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
    sorted_issues = sorted(issues, key=lambda x: (severity_order[x.severity], x.file, x.start_line))

    for issue in sorted_issues:
        severity_label = f"[{issue.severity.value}]"
        print(
            f"\n{severity_label} {issue.file}:{issue.start_line}-{issue.end_line}  {issue.function_name}()"
        )
        print(f"  - {issue.message}")


def print_issues_with_explanations(issues, verbose=True, summary=False):
    """Print issues with detailed explanations (V5).

    Args:
        issues: List of issues to print
        verbose: If True, show full explanations with examples
        summary: If True, show brief explanations only
    """
    if not issues:
        print("\n✓ No issues found! Your code looks good.\n")
        return

    # Sort by severity
    severity_order = {Severity.CRITICAL: 0, Severity.WARN: 1, Severity.INFO: 2}
    sorted_issues = sorted(issues, key=lambda x: (severity_order[x.severity], x.file, x.start_line))

    print("\n" + "=" * 80)
    print(f"Found {len(issues)} issue(s) with detailed explanations")
    print("=" * 80 + "\n")

    for _, issue in enumerate(sorted_issues, 1):
        explanation = get_explanation(issue)

        # Print detailed explanation
        print(format_explanation(issue, explanation, verbose=verbose and not summary))

        # Add severity guidance for critical/warning issues
        if issue.severity in (Severity.CRITICAL, Severity.WARN) and verbose:
            print(get_severity_guidance(issue.severity).strip())
            print("\n" + "=" * 80 + "\n")


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
        "issues": [issue.to_dict() for issue in issues],
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
