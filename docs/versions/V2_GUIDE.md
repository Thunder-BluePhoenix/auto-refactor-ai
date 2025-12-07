# V2 Implementation Guide

## Overview

V2 adds **configuration file support** and **JSON output mode**, transforming the analyzer from a simple CLI tool into a professional-grade solution ready for CI/CD integration and IDE tooling.

## What You'll Learn

- Configuration management patterns
- TOML and YAML parsing
- JSON serialization
- File system traversal for config discovery
- Priority and override systems
- Data modeling with dataclasses

## Prerequisites

- Completed V1 (multiple rules with severity levels)
- Basic understanding of TOML/YAML formats
- Familiarity with JSON

## Implementation Steps

### Step 1: Create Configuration Dataclass

```python
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class Config:
    """Configuration settings for the analyzer."""
    max_function_length: int = 30
    max_parameters: int = 5
    max_nesting_depth: int = 3
    enabled_rules: list = None

    def __post_init__(self):
        if self.enabled_rules is None:
            self.enabled_rules = ["function-too-long", "too-many-parameters", "deep-nesting"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        valid_keys = {
            "max_function_length", "max_parameters", "max_nesting_depth", "enabled_rules"
        }
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)
```

**Why Dataclasses?**
- Automatic `__init__`, `__repr__`, `__eq__`
- Type hints for better IDE support
- Easy conversion to/from dicts

### Step 2: Implement TOML Parser

For Python 3.11+, use built-in `tomllib`. For older versions, we need a fallback:

```python
def load_toml_config(path: Path) -> Optional[Dict[str, Any]]:
    """Load configuration from a TOML file."""
    try:
        # Python 3.11+ has built-in tomllib
        try:
            import tomllib
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except ImportError:
            # Fallback: simple TOML parser for basic cases
            data = _parse_simple_toml(path)

        # Check if it's pyproject.toml
        if path.name == "pyproject.toml":
            return data.get("tool", {}).get("auto-refactor-ai", {})
        return data

    except Exception as e:
        print(f"[WARNING] Could not load TOML config from {path}: {e}")
        return None
```

**Fallback Parser for Python < 3.11:**

```python
def _parse_simple_toml(path: Path) -> Dict[str, Any]:
    """Simple TOML parser for basic key=value pairs."""
    config = {}
    current_section = config

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Section header: [tool.auto-refactor-ai]
            if line.startswith("[") and line.endswith("]"):
                section_name = line[1:-1].strip()
                # Handle nested sections
                parts = section_name.split(".")
                current_section = config
                for part in parts:
                    if part not in current_section:
                        current_section[part] = {}
                    current_section = current_section[part]
                continue

            # Key-value pair
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Parse value types
                if value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                elif value.startswith("[") and value.endswith("]"):
                    # Simple list parsing
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(",") if v.strip()]
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass

                current_section[key] = value

    return config
```

**Key Concepts:**
- Binary mode (`"rb"`) for `tomllib`
- Text mode for fallback parser
- Nested section handling with `split(".")`
- Type inference for integers, booleans, lists

### Step 3: Implement Config File Discovery

```python
def find_config_file(start_path: Path = None) -> Optional[Path]:
    """
    Search for a configuration file starting from start_path and moving up.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Search upward through directories
    while True:
        # Check for dedicated config files
        for filename in [".auto-refactor-ai.toml", ".auto-refactor-ai.yaml", ".auto-refactor-ai.yml"]:
            config_path = current / filename
            if config_path.exists():
                return config_path

        # Check for pyproject.toml with our section
        pyproject_path = current / "pyproject.toml"
        if pyproject_path.exists():
            data = load_toml_config(pyproject_path)
            if data:  # Only return if it has our config section
                return pyproject_path

        # Move up one directory
        parent = current.parent
        if parent == current:  # Reached root
            break
        current = parent

    return None
```

**Directory Traversal Pattern:**
1. Start at current directory
2. Check for config files
3. Move to parent directory
4. Repeat until root reached

### Step 4: Add JSON Serialization to Issue

```python
@dataclass
class Issue:
    # ... existing fields ...

    def to_dict(self):
        """Convert issue to dictionary for JSON serialization."""
        return {
            "severity": self.severity.value,  # Convert Enum to string
            "file": self.file,
            "function_name": self.function_name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "rule_name": self.rule_name,
            "message": self.message,
            "details": self.details or {}
        }
```

**Important:** Convert Enum to `.value` for JSON compatibility.

### Step 5: Implement JSON Output

```python
import json

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
```

**JSON Structure:**
```json
{
  "config": { ... },
  "summary": {
    "total": 10,
    "critical": 1,
    "warn": 4,
    "info": 5
  },
  "issues": [ ... ]
}
```

### Step 6: Update CLI

Add new arguments:

```python
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
```

Load config with priority system:

```python
# Load configuration
config = load_config(Path(args.config) if args.config else None)

# Command-line arguments override config file
if args.max_len is not None:
    config.max_function_length = args.max_len
if args.max_params is not None:
    config.max_parameters = args.max_params
if args.max_nesting is not None:
    config.max_nesting_depth = args.max_nesting
```

**Priority System:**
1. Command-line arguments (highest)
2. Config file specified with `--config`
3. Auto-discovered config file
4. Default values (lowest)

### Step 7: Create Sample Config Files

**.auto-refactor-ai.toml:**
```toml
# Maximum allowed function length in lines
max_function_length = 30

# Maximum allowed number of parameters per function
max_parameters = 5

# Maximum allowed nesting depth
max_nesting_depth = 3

# List of enabled rules
enabled_rules = ["function-too-long", "too-many-parameters", "deep-nesting"]
```

**pyproject.toml integration:**
```toml
[tool.auto-refactor-ai]
max_function_length = 30
max_parameters = 5
max_nesting_depth = 3
```

**.auto-refactor-ai.yaml:**
```yaml
max_function_length: 30
max_parameters: 5
max_nesting_depth: 3

enabled_rules:
  - function-too-long
  - too-many-parameters
  - deep-nesting
```

## Testing V2

### Test Config File Discovery

```bash
# Should find .auto-refactor-ai.toml in current directory
python -m auto_refactor_ai test_files/

# Use specific config
python -m auto_refactor_ai test_files/ --config examples/config-strict.toml

# CLI overrides config
python -m auto_refactor_ai test_files/ --max-len 20
```

### Test JSON Output

```bash
# Get JSON output
python -m auto_refactor_ai test_files/test_perfect_code.py --format json

# Pipe to jq for pretty printing
python -m auto_refactor_ai test_files/ --format json | jq '.summary'

# Save to file for CI/CD
python -m auto_refactor_ai . --format json > analysis.json
```

### Test Priority System

Create `.auto-refactor-ai.toml` with `max_function_length = 25`:

```bash
# Uses config file (25)
python -m auto_refactor_ai test_files/

# CLI overrides (20)
python -m auto_refactor_ai test_files/ --max-len 20
```

## Use Cases

### 1. CI/CD Integration

```yaml
# .github/workflows/quality.yml
- name: Analyze Code
  run: |
    python -m auto_refactor_ai . --format json > analysis.json

- name: Check for Critical Issues
  run: |
    CRITICAL=$(jq '.summary.critical' analysis.json)
    if [ "$CRITICAL" -gt "0" ]; then
      echo "Found $CRITICAL critical issues!"
      exit 1
    fi
```

### 2. IDE Extension

```python
# Get issues as structured data
result = subprocess.run([
    "auto-refactor-ai",
    "current_file.py",
    "--format", "json"
], capture_output=True)

data = json.loads(result.stdout)
for issue in data["issues"]:
    # Show in IDE problems panel
    show_problem(
        file=issue["file"],
        line=issue["start_line"],
        severity=issue["severity"],
        message=issue["message"]
    )
```

### 3. Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Get list of Python files being committed
FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$FILES" ]; then
    python -m auto_refactor_ai $FILES --format json > /tmp/analysis.json
    CRITICAL=$(jq '.summary.critical' /tmp/analysis.json)

    if [ "$CRITICAL" -gt "0" ]; then
        echo "❌ Commit blocked: $CRITICAL critical code quality issues found"
        jq '.issues[] | select(.severity == "CRITICAL")' /tmp/analysis.json
        exit 1
    fi
fi
```

## Architecture Insights

### Config Loading Flow

```
1. Check --config argument
   ├─ If specified → Load that file
   └─ If not specified → Auto-discover
       ├─ Check current dir for .auto-refactor-ai.toml
       ├─ Check current dir for .auto-refactor-ai.yaml
       ├─ Check current dir for pyproject.toml
       ├─ Move to parent directory
       └─ Repeat until root

2. Load config from file

3. Apply CLI overrides
   ├─ --max-len overrides max_function_length
   ├─ --max-params overrides max_parameters
   └─ --max-nesting overrides max_nesting_depth

4. Use final config for analysis
```

### JSON vs Text Output

**Text Output** (for humans):
- Colored/formatted output
- Sorted by severity
- Summary table
- Readable messages

**JSON Output** (for machines):
- Structured data
- Machine-parseable
- Complete metadata
- No formatting

## Common Pitfalls

### 1. Forgetting to Convert Enums

```python
# ❌ Wrong: Can't serialize Enum directly
json.dumps({"severity": Severity.CRITICAL})  # TypeError!

# ✅ Correct: Convert to value
json.dumps({"severity": Severity.CRITICAL.value})  # "CRITICAL"
```

### 2. Not Handling Missing Config Sections

```python
# ❌ Wrong: KeyError if section missing
data = load_toml("pyproject.toml")
return data["tool"]["auto-refactor-ai"]  # KeyError!

# ✅ Correct: Use .get() with defaults
return data.get("tool", {}).get("auto-refactor-ai", {})
```

### 3. Binary vs Text Mode

```python
# ❌ Wrong: Text mode for tomllib
import tomllib
with open(path, "r") as f:  # Should be "rb"!
    tomllib.load(f)

# ✅ Correct: Binary mode
with open(path, "rb") as f:
    tomllib.load(f)
```

## Exercises

1. **Add YAML support**: Implement `load_yaml_config()` with PyYAML
2. **Add config validation**: Check for invalid threshold values
3. **Add `--init` command**: Generate default config file
4. **Add output to file**: `--output analysis.json`

## Next Steps

In V3, we'll make the package pip-installable:
- Proper `pyproject.toml` setup
- Console script entry points
- Package distribution

## Key Takeaways

✅ **Config files** enable per-project settings
✅ **Auto-discovery** improves user experience
✅ **Priority systems** provide flexibility
✅ **JSON output** enables tooling integration
✅ **Fallback parsers** maintain compatibility
✅ **Structured output** supports automation
