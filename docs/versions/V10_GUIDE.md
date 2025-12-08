# V10 Implementation Guide: Refactor Planning Mode

## Overview

V10 adds strategic refactoring planning capabilities. Instead of just listing issues, the tool now generates prioritized roadmaps with effort/impact analysis and optional AI-powered strategic advice.

## Goals

1. Generate strategic refactoring plans
2. Prioritize issues by severity, effort, and impact
3. Identify quick wins (low-effort, high-value)
4. Integrate LLM for strategic advice
5. Output reports in multiple formats (text, markdown, HTML)

## New CLI Flags (V10)

| Flag | Description | Default |
|------|-------------|---------|
| `--plan` | Enable refactor planning mode | False |
| `--plan-format` | Output format: text, markdown, html | text |
| `--output` / `-o` | Save report to file | None |

## Usage

```bash
# Basic text plan
auto-refactor-ai . --plan

# Markdown plan
auto-refactor-ai . --plan --plan-format markdown

# HTML report saved to file
auto-refactor-ai . --plan --plan-format html -o report.html

# With AI strategic advice
auto-refactor-ai . --plan --ai-suggestions

# Full example
auto-refactor-ai . --plan --plan-format html --ai-suggestions -o refactor-report.html
```

## Architecture

### New Module: `refactor_planner.py`

```python
@dataclass
class PlanMetric:
    """Aggregated metrics for the codebase."""
    total_files: int
    total_functions: int
    total_issues: int
    critical_count: int
    warning_count: int
    info_count: int
    duplicate_count: int
    average_complexity_score: float

@dataclass
class RefactorItem:
    """A single item in the refactoring plan."""
    priority_score: float
    issue: Issue
    file_path: str
    function_name: str
    description: str
    effort: str  # "Low", "Medium", "High"
    impact: str  # "Low", "Medium", "High"

@dataclass
class RefactorPlan:
    """Complete refactoring plan."""
    executive_summary: str
    metrics: PlanMetric
    critical_hotspots: List[RefactorItem]
    quick_wins: List[RefactorItem]
    strategic_roadmap: List[str]
    llm_advice: Optional[str] = None

class RefactorPlanner:
    """Planner to generate strategic refactoring roadmaps."""
    
    def generate_plan(include_llm_advice: bool, llm_config: LLMConfig) -> RefactorPlan
    def format_plan(plan: RefactorPlan, format_type: str) -> str
```

### Priority Scoring Algorithm

Issues are scored based on:
1. **Severity**: CRITICAL=100, WARN=50, INFO=10
2. **Rule type multipliers**: deep-nesting ×1.2, too-many-parameters ×1.1
3. **Quick win detection**: Low effort for INFO or small violations

### HTML Report Features

- Dark theme design (#0d1117 background)
- Metrics grid with color-coded values
- Roadmap with visual phases
- Hotspot cards with impact/effort
- Quick wins section
- AI advice section (if enabled)

## Testing

```bash
# Run V10 tests
pytest tests/test_refactor_planner.py tests/test_refactor_planner_v10.py -v

# All tests (289 total)
pytest tests/ -v --no-cov
```

## Output Examples

### Text Format
```
[REFACTORING PLAN]
==================================================
Analyzed 12 files. Found 45 issues. Codebase Health: Needs Attention.
--------------------------------------------------
Critical: 5 | Warnings: 15
Duplicates: 2

STRATEGIC ROADMAP:
  • Phase 1: Architecture - Consolidate 2 duplicate groups.
  • Phase 2: Quick Wins - Fix 5 low-effort issues.
  • Phase 3: Deep Dives - Refactor top critical hotspots.
  • Phase 4: Maintenance - Address remaining warnings.

TOP 5 HOTSPOTS:
  • process_data (utils.py) - High Impact
  ...
```

### HTML Format
Generates a standalone HTML document with modern dark theme styling.

---

**V10 Status:** ✅ COMPLETE
**Next:** V11 - IDE/Editor Integration
