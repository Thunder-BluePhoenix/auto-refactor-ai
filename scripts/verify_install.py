#!/usr/bin/env python3
"""
Verification script to test auto-refactor-ai installation.
Run after installing the package.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_import():
    """Test 1: Check if package can be imported."""
    print("Test 1: Checking imports...")
    try:
        import auto_refactor_ai
        from auto_refactor_ai.analyzer import Issue, Severity, analyze_file
        from auto_refactor_ai.cli import main
        from auto_refactor_ai.config import Config, load_config
        print("  ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_command_exists():
    """Test 2: Check if auto-refactor-ai command exists."""
    print("\nTest 2: Checking command availability...")
    try:
        result = subprocess.run(
            ["auto-refactor-ai", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("  ✅ Command 'auto-refactor-ai' works")
            return True
        else:
            print(f"  ❌ Command failed with code {result.returncode}")
            return False
    except FileNotFoundError:
        print("  ❌ Command 'auto-refactor-ai' not found")
        print("     Try: pip install -e . or pip install dist/*.whl")
        return False
    except Exception as e:
        print(f"  ❌ Error running command: {e}")
        return False


def test_file_analysis():
    """Test 3: Test analyzing a file."""
    print("\nTest 3: Testing file analysis...")
    try:
        from auto_refactor_ai.analyzer import analyze_file

        # Test with a simple good code snippet
        test_code = '''
def simple_function(x, y):
    """A simple function."""
    return x + y
'''
        # Write temporary test file
        test_file = Path("_test_temp.py")
        test_file.write_text(test_code)

        try:
            issues = analyze_file(str(test_file))
            if len(issues) == 0:
                print("  ✅ File analysis works (no issues in good code)")
                return True
            else:
                print(f"  ⚠️  Found {len(issues)} issues in simple code (unexpected)")
                return True  # Still works, just unexpected
        finally:
            test_file.unlink(missing_ok=True)

    except Exception as e:
        print(f"  ❌ File analysis failed: {e}")
        return False


def test_json_output():
    """Test 4: Test JSON output mode."""
    print("\nTest 4: Testing JSON output...")
    try:
        # Create a temp test file
        test_file = Path("_test_temp.py")
        test_file.write_text("def x(): pass")

        try:
            result = subprocess.run(
                ["auto-refactor-ai", str(test_file), "--format", "json"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Verify it's valid JSON
                data = json.loads(result.stdout)
                if "config" in data and "summary" in data and "issues" in data:
                    print("  ✅ JSON output works")
                    return True
                else:
                    print("  ❌ JSON structure missing required fields")
                    return False
            else:
                print(f"  ❌ Command failed: {result.stderr}")
                return False
        finally:
            test_file.unlink(missing_ok=True)

    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON output: {e}")
        return False
    except Exception as e:
        print(f"  ❌ JSON test failed: {e}")
        return False


def test_config_loading():
    """Test 5: Test config file loading."""
    print("\nTest 5: Testing config loading...")
    try:
        from auto_refactor_ai.config import Config, load_config

        # Test default config
        config = load_config(None)
        if isinstance(config, Config):
            print(f"  ✅ Config loads: max_len={config.max_function_length}, "
                  f"max_params={config.max_parameters}, "
                  f"max_nesting={config.max_nesting_depth}")
            return True
        else:
            print("  ❌ Config is not a Config object")
            return False
    except Exception as e:
        print(f"  ❌ Config loading failed: {e}")
        return False


def test_cli_args():
    """Test 6: Test CLI argument parsing."""
    print("\nTest 6: Testing CLI arguments...")
    try:
        test_file = Path("_test_temp.py")
        test_file.write_text("def x(): pass")

        try:
            # Test with custom parameters
            result = subprocess.run(
                ["auto-refactor-ai", str(test_file), "--max-len", "10", "--max-params", "2"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print("  ✅ CLI arguments work")
                return True
            else:
                print(f"  ❌ CLI args failed: {result.stderr}")
                return False
        finally:
            test_file.unlink(missing_ok=True)

    except Exception as e:
        print(f"  ❌ CLI args test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Auto Refactor AI - Installation Verification")
    print("=" * 60)

    tests = [
        test_import,
        test_command_exists,
        test_file_analysis,
        test_json_output,
        test_config_loading,
        test_cli_args,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n  ❌ Test crashed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"  Passed: {passed}/{total}")
    print(f"  Failed: {total - passed}/{total}")

    if all(results):
        print("\n🎉 All tests passed! Installation is working correctly.")
        print("=" * 60)
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
