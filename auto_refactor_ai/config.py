"""
Configuration management for auto-refactor-ai.

Supports loading configuration from:
- .auto-refactor-ai.toml (TOML format)
- .auto-refactor-ai.yaml or .auto-refactor-ai.yml (YAML format)
- pyproject.toml under [tool.auto-refactor-ai] section
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class Config:
    """Configuration settings for the analyzer."""

    max_function_length: int = 30
    max_parameters: int = 5
    max_nesting_depth: int = 3
    enabled_rules: Optional[List[str]] = None  # None means all rules enabled

    def __post_init__(self):
        if self.enabled_rules is None:
            self.enabled_rules = ["function-too-long", "too-many-parameters", "deep-nesting"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        valid_keys = {"max_function_length", "max_parameters", "max_nesting_depth", "enabled_rules"}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


def load_toml_config(path: Path) -> Optional[Dict[str, Any]]:
    """
    Load configuration from a TOML file.
    Uses standard library tomllib (Python 3.11+) or fallback parser.
    """
    try:
        # Python 3.11+ has built-in tomllib
        try:
            import tomllib  # type: ignore[import-not-found]

            with open(path, "rb") as f:
                data: Dict[str, Any] = tomllib.load(f)
        except ImportError:
            # Fallback: simple TOML parser for basic cases
            data = _parse_simple_toml(path)

        # Check if it's pyproject.toml
        if path.name == "pyproject.toml":
            tool_data = data.get("tool", {})
            if isinstance(tool_data, dict):
                result = tool_data.get("auto-refactor-ai", {})
                return dict(result) if result else {}
            return {}
        return dict(data)

    except Exception as e:
        print(f"[WARNING] Could not load TOML config from {path}: {e}")
        return None


def _parse_simple_toml(path: Path) -> Dict[str, Any]:
    """
    Simple TOML parser for basic key=value pairs.
    This is a fallback for Python < 3.11 without external dependencies.
    """
    config: Dict[str, Any] = {}
    current_section: Dict[str, Any] = config

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Section header
            if line.startswith("[") and line.endswith("]"):
                section_name = line[1:-1].strip()
                # Handle nested sections like [tool.auto-refactor-ai]
                parts = section_name.split(".")
                current_section = config
                for part in parts:
                    if part not in current_section:
                        current_section[part] = {}
                    current_section = current_section[part]
                continue

            # Key-value pair
            if "=" in line:
                key, value_str = line.split("=", 1)
                key = key.strip()
                value_str = value_str.strip()
                parsed_value: Union[str, bool, int, float, List[str]] = value_str

                # Parse value
                if value_str.lower() in ("true", "false"):
                    parsed_value = value_str.lower() == "true"
                elif value_str.startswith("[") and value_str.endswith("]"):
                    # Simple list parsing
                    parsed_value = [v.strip().strip("\"'") for v in value_str[1:-1].split(",") if v.strip()]
                elif value_str.startswith('"') and value_str.endswith('"'):
                    parsed_value = value_str[1:-1]
                elif value_str.startswith("'") and value_str.endswith("'"):
                    parsed_value = value_str[1:-1]
                else:
                    try:
                        parsed_value = int(value_str)
                    except ValueError:
                        try:
                            parsed_value = float(value_str)
                        except ValueError:
                            parsed_value = value_str

                current_section[key] = parsed_value

    return config


def load_yaml_config(path: Path) -> Optional[Dict[str, Any]]:
    """
    Load configuration from a YAML file.
    Uses PyYAML if available, otherwise falls back to JSON-like parsing.
    """
    try:
        try:
            import yaml  # type: ignore[import-untyped]

            with open(path, encoding="utf-8") as f:
                result = yaml.safe_load(f)
                return dict(result) if result else None
        except ImportError:
            # Fallback: Use JSON parser for simple YAML files
            with open(path, encoding="utf-8") as f:
                # This only works for JSON-compatible YAML
                content = f.read()
                return dict(json.loads(content))

    except Exception as e:
        print(f"[WARNING] Could not load YAML config from {path}: {e}")
        return None


def find_config_file(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Search for a configuration file starting from start_path and moving up.
    Looks for (in order):
    1. .auto-refactor-ai.toml
    2. .auto-refactor-ai.yaml
    3. .auto-refactor-ai.yml
    4. pyproject.toml (with [tool.auto-refactor-ai] section)
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Search upward through directories
    while True:
        # Check for dedicated config files
        for filename in [
            ".auto-refactor-ai.toml",
            ".auto-refactor-ai.yaml",
            ".auto-refactor-ai.yml",
        ]:
            config_path = current / filename
            if config_path.exists():
                return config_path

        # Check for pyproject.toml
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


def load_config(path: Optional[Path] = None) -> Config:
    """
    Load configuration from file or use defaults.

    Args:
        path: Optional path to config file. If None, searches for config automatically.

    Returns:
        Config object with settings
    """
    # If no path provided, search for config file
    if path is None:
        path = find_config_file()

    # If still no config file found, use defaults
    if path is None:
        return Config()

    # Load config based on file extension
    if path.suffix == ".toml":
        data = load_toml_config(path)
    elif path.suffix in (".yaml", ".yml"):
        data = load_yaml_config(path)
    else:
        print(f"[WARNING] Unknown config file format: {path}")
        return Config()

    # Return default config if loading failed
    if data is None:
        return Config()

    # Create config from loaded data
    try:
        return Config.from_dict(data)
    except Exception as e:
        print(f"[WARNING] Invalid config format: {e}")
        return Config()
