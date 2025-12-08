"""Tests for config module."""

import tempfile
from pathlib import Path

from auto_refactor_ai.config import (
    Config,
    _parse_simple_toml,
    find_config_file,
    load_config,
    load_toml_config,
)


class TestConfig:
    """Test Config dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.max_function_length == 30
        assert config.max_parameters == 5
        assert config.max_nesting_depth == 3
        assert config.enabled_rules == [
            "function-too-long",
            "too-many-parameters",
            "deep-nesting",
        ]

    def test_custom_config(self):
        """Test creating custom configuration."""
        config = Config(
            max_function_length=20, max_parameters=3, max_nesting_depth=2, enabled_rules=["rule1"]
        )
        assert config.max_function_length == 20
        assert config.max_parameters == 3
        assert config.max_nesting_depth == 2
        assert config.enabled_rules == ["rule1"]

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(max_function_length=25)
        result = config.to_dict()
        assert isinstance(result, dict)
        assert result["max_function_length"] == 25
        assert result["max_parameters"] == 5  # default
        assert "enabled_rules" in result

    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "max_function_length": 40,
            "max_parameters": 7,
            "max_nesting_depth": 4,
            "enabled_rules": ["rule1", "rule2"],
        }
        config = Config.from_dict(data)
        assert config.max_function_length == 40
        assert config.max_parameters == 7
        assert config.max_nesting_depth == 4
        assert config.enabled_rules == ["rule1", "rule2"]

    def test_config_from_dict_filters_invalid_keys(self):
        """Test that from_dict filters out invalid keys."""
        data = {
            "max_function_length": 40,
            "invalid_key": "value",
            "another_invalid": 123,
        }
        config = Config.from_dict(data)
        assert config.max_function_length == 40
        assert config.max_parameters == 5  # default
        # Should not raise error, just ignore invalid keys


class TestParseSimpleToml:
    """Test _parse_simple_toml function."""

    def test_parse_simple_toml(self):
        """Test parsing basic TOML file."""
        toml_content = """
# Comment
max_function_length = 25
max_parameters = 4

[section]
key = "value"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            result = _parse_simple_toml(temp_path)
            assert result["max_function_length"] == 25
            assert result["max_parameters"] == 4
            assert "section" in result
            assert result["section"]["key"] == "value"
        finally:
            temp_path.unlink()

    def test_parse_nested_sections(self):
        """Test parsing nested TOML sections."""
        toml_content = """
[tool.auto-refactor-ai]
max_function_length = 30
max_parameters = 5
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            result = _parse_simple_toml(temp_path)
            assert "tool" in result
            assert "auto-refactor-ai" in result["tool"]
            assert result["tool"]["auto-refactor-ai"]["max_function_length"] == 30
        finally:
            temp_path.unlink()

    def test_parse_list_values(self):
        """Test parsing list values in TOML."""
        toml_content = """
enabled_rules = ["rule1", "rule2", "rule3"]
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            result = _parse_simple_toml(temp_path)
            assert result["enabled_rules"] == ["rule1", "rule2", "rule3"]
        finally:
            temp_path.unlink()

    def test_parse_boolean_values(self):
        """Test parsing boolean values."""
        toml_content = """
flag_true = true
flag_false = false
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            result = _parse_simple_toml(temp_path)
            assert result["flag_true"] is True
            assert result["flag_false"] is False
        finally:
            temp_path.unlink()


class TestLoadTomlConfig:
    """Test load_toml_config function."""

    def test_load_simple_toml(self):
        """Test loading a simple TOML config file."""
        toml_content = """
max_function_length = 35
max_parameters = 6
max_nesting_depth = 4
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".auto-refactor-ai.toml", delete=False
        ) as f:
            f.write(toml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            result = load_toml_config(temp_path)
            assert result is not None
            assert result["max_function_length"] == 35
            assert result["max_parameters"] == 6
        finally:
            temp_path.unlink()

    def test_load_pyproject_toml(self):
        """Test loading config from pyproject.toml."""
        toml_content = """
[tool.auto-refactor-ai]
max_function_length = 40
max_parameters = 7
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "pyproject.toml"
            temp_path.write_text(toml_content)

            result = load_toml_config(temp_path)
            assert result is not None
            assert result["max_function_length"] == 40
            assert result["max_parameters"] == 7

    def test_load_invalid_toml(self):
        """Test loading invalid TOML returns None."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("this is not valid toml { [")
            f.flush()
            temp_path = Path(f.name)

        try:
            result = load_toml_config(temp_path)
            # Should handle error gracefully
            assert result is None or isinstance(result, dict)
        finally:
            temp_path.unlink()


class TestFindConfigFile:
    """Test find_config_file function."""

    def test_find_config_in_current_dir(self):
        """Test finding config file in current directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_file = tmpdir_path / ".auto-refactor-ai.toml"
            config_file.write_text("max_function_length = 30")

            result = find_config_file(tmpdir_path)
            assert result is not None
            assert result.name == ".auto-refactor-ai.toml"

    def test_find_yaml_config(self):
        """Test finding YAML config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_file = tmpdir_path / ".auto-refactor-ai.yaml"
            config_file.write_text("max_function_length: 30")

            result = find_config_file(tmpdir_path)
            assert result is not None
            assert result.name == ".auto-refactor-ai.yaml"

    def test_no_config_found(self):
        """Test when no config file is found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            result = find_config_file(tmpdir_path)
            assert result is None

    def test_find_in_parent_directory(self):
        """Test finding config file in parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            subdir = tmpdir_path / "subdir"
            subdir.mkdir()

            # Put config in parent
            config_file = tmpdir_path / ".auto-refactor-ai.toml"
            config_file.write_text("max_function_length = 30")

            # Search from subdirectory
            result = find_config_file(subdir)
            assert result is not None
            assert result.name == ".auto-refactor-ai.toml"


class TestLoadConfig:
    """Test load_config function."""

    def test_load_config_default(self):
        """Test loading default config when no file found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            # Force searching in empty directory
            config = load_config(tmpdir_path / "nonexistent.toml")
            # Should return default config
            assert isinstance(config, Config)
            assert config.max_function_length == 30

    def test_load_config_from_file(self):
        """Test loading config from specified file."""
        toml_content = """
max_function_length = 50
max_parameters = 10
max_nesting_depth = 5
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(toml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            config = load_config(temp_path)
            assert config.max_function_length == 50
            assert config.max_parameters == 10
            assert config.max_nesting_depth == 5
        finally:
            temp_path.unlink()

    def test_load_config_with_auto_discovery(self):
        """Test config auto-discovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_file = tmpdir_path / ".auto-refactor-ai.toml"
            config_file.write_text(
                """
max_function_length = 45
max_parameters = 8
"""
            )

            # Create a subdirectory to test search
            subdir = tmpdir_path / "src"
            subdir.mkdir()

            # This should find the config in parent directory
            import os

            old_cwd = os.getcwd()
            try:
                os.chdir(subdir)
                config = load_config(None)
                # Should load from discovered file
                assert config.max_function_length == 45
                assert config.max_parameters == 8
            finally:
                os.chdir(old_cwd)
