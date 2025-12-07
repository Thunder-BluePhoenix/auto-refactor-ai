# V3 Implementation Guide

## Overview

V3 transforms your analyzer into a **proper Python package** that can be installed with `pip install auto-refactor-ai`. Users will be able to run it as a command-line tool without `python -m`.

## What You'll Learn

- Python packaging with `pyproject.toml`
- Console script entry points
- Package distribution
- Semantic versioning
- File manifests
- Building and installing packages
- Publishing to PyPI/TestPyPI

## Prerequisites

- Completed V2 (config files + JSON output)
- Basic understanding of pip and virtual environments
- Familiarity with package installation

## Implementation Steps

### Step 1: Update pyproject.toml for Packaging

Transform `pyproject.toml` into a proper package configuration:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "auto-refactor-ai"
version = "0.3.0"  # V3 version!
description = "A beginner-friendly static analyzer for Python code with configurable rules"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
keywords = ["refactoring", "static-analysis", "code-quality", "linting", "ast"]
authors = [
    {name = "Auto Refactor AI Contributors", email = "auto-refactor-ai@example.com"}
]
maintainers = [
    {name = "Auto Refactor AI Contributors", email = "auto-refactor-ai@example.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Quality Assurance",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Operating System :: OS Independent",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
]

[project.scripts]
auto-refactor-ai = "auto_refactor_ai.cli:main"

[project.urls]
Homepage = "https://github.com/yourusername/auto-refactor-ai"
Repository = "https://github.com/yourusername/auto-refactor-ai"
Issues = "https://github.com/yourusername/auto-refactor-ai/issues"
Documentation = "https://github.com/yourusername/auto-refactor-ai#readme"
Changelog = "https://github.com/yourusername/auto-refactor-ai/blob/main/CHANGELOG.md"

[tool.setuptools.packages.find]
where = ["."]
include = ["auto_refactor_ai*"]
exclude = ["tests*", "test_files*", "examples*"]
```

**Key Components Explained:**

#### Build System
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```
- Specifies build tools needed
- `setuptools` is the build system
- `wheel` for creating wheel distributions

#### Version and Metadata
```toml
version = "0.3.0"
```
- Follow semantic versioning: MAJOR.MINOR.PATCH
- V0 = 0.0.x, V1 = 0.1.x, V2 = 0.2.x, V3 = 0.3.x

#### Classifiers
```toml
classifiers = [
    "Development Status :: 4 - Beta",
    ...
]
```
- Help users find your package on PyPI
- Indicate stability, audience, topic
- See: https://pypi.org/classifiers/

#### Console Scripts (IMPORTANT!)
```toml
[project.scripts]
auto-refactor-ai = "auto_refactor_ai.cli:main"
```
- Creates `auto-refactor-ai` command
- Points to `main()` function in `cli.py`
- Users can run `auto-refactor-ai` instead of `python -m auto_refactor_ai`

### Step 2: Create LICENSE File

Every package needs a license. We use MIT:

```text
MIT License

Copyright (c) 2025 Auto Refactor AI Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Save as `LICENSE` (no extension).

### Step 3: Create MANIFEST.in

Controls which files are included in the distribution:

```
# Include documentation
include README.md
include LICENSE
include CHANGELOG.md

# Include configuration examples
recursive-include examples *.toml *.yaml *.yml

# Exclude test files from distribution
recursive-exclude test_files *
recursive-exclude tests *

# Exclude development files
exclude .gitignore
exclude .auto-refactor-ai.toml
```

**Why MANIFEST.in?**
- Controls extra files beyond Python modules
- Include docs, examples, config files
- Exclude tests, development files
- Keeps package size reasonable

### Step 4: Verify Package Structure

Your directory should look like:

```
auto-refactor-ai/
├── auto_refactor_ai/
│   ├── __init__.py
│   ├── __main__.py
│   ├── analyzer.py
│   ├── cli.py
│   └── config.py
├── examples/
│   ├── config-strict.toml
│   ├── config-relaxed.toml
│   └── .auto-refactor-ai.yaml
├── test_files/
│   └── ... (test files)
├── docs/
│   └── ... (documentation)
├── pyproject.toml
├── LICENSE
├── MANIFEST.in
├── README.md
└── CHANGELOG.md
```

### Step 5: Build the Package

```bash
# Install build tools
pip install build

# Build the package
python -m build
```

This creates:
- `dist/auto_refactor_ai-0.3.0.tar.gz` (source distribution)
- `dist/auto_refactor_ai-0.3.0-py3-none-any.whl` (wheel distribution)

**Wheel vs Source Distribution:**
- **Wheel (.whl)**: Pre-built, faster to install
- **Source (.tar.gz)**: Source code, built during install

### Step 6: Test Local Installation

```bash
# Create a new virtual environment for testing
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from local wheel
pip install dist/auto_refactor_ai-0.3.0-py3-none-any.whl

# Test the command works
auto-refactor-ai --help
auto-refactor-ai --version  # If you add this

# Test analysis
auto-refactor-ai test_files/test_perfect_code.py

# Test JSON output
auto-refactor-ai test_files/ --format json

# Deactivate and clean up
deactivate
rm -rf test_env
```

### Step 7: Verify Installation

Create a verification script:

```bash
#!/bin/bash
# verify_install.sh

echo "Testing auto-refactor-ai installation..."

# Test 1: Command exists
if command -v auto-refactor-ai &> /dev/null; then
    echo "✅ Command 'auto-refactor-ai' found"
else
    echo "❌ Command 'auto-refactor-ai' not found"
    exit 1
fi

# Test 2: Help works
if auto-refactor-ai --help &> /dev/null; then
    echo "✅ Help command works"
else
    echo "❌ Help command failed"
    exit 1
fi

# Test 3: Can analyze file
if auto-refactor-ai test_files/test_perfect_code.py &> /dev/null; then
    echo "✅ File analysis works"
else
    echo "❌ File analysis failed"
    exit 1
fi

# Test 4: JSON output works
if auto-refactor-ai test_files/test_perfect_code.py --format json | python -m json.tool &> /dev/null; then
    echo "✅ JSON output works"
else
    echo "❌ JSON output failed"
    exit 1
fi

echo ""
echo "🎉 All tests passed!"
```

### Step 8: Publish to TestPyPI (Optional)

TestPyPI is a sandbox for testing package uploads:

```bash
# Install twine for uploading
pip install twine

# Create account at https://test.pypi.org/

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ auto-refactor-ai
```

### Step 9: Publish to PyPI (When Ready)

**Only do this when ready for public release!**

```bash
# Create account at https://pypi.org/

# Upload to PyPI
python -m twine upload dist/*

# Now anyone can install with:
# pip install auto-refactor-ai
```

## Package Development Workflow

### Making Changes

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Make code changes
4. Rebuild: `python -m build`
5. Test locally
6. Upload to TestPyPI (optional)
7. Upload to PyPI

### Version Numbers

Follow semantic versioning:
- **0.x.y** - Initial development
  - 0.0.x - V0 (alpha)
  - 0.1.x - V1 (alpha)
  - 0.2.x - V2 (beta)
  - 0.3.x - V3 (beta)
- **1.0.0** - First stable release
- **1.1.0** - New features (backward compatible)
- **2.0.0** - Breaking changes

### Adding Dependencies

If you need external packages:

```toml
[project]
dependencies = [
    "click>=8.0",  # Example dependency
    "rich>=10.0",
]
```

We intentionally have **zero dependencies** for now!

## Testing the Installed Package

### Import Test

```python
# test_import.py
import auto_refactor_ai
from auto_refactor_ai.analyzer import analyze_file
from auto_refactor_ai.config import load_config

print("✅ All imports successful")
```

### Functional Test

```python
# test_functional.py
from auto_refactor_ai.analyzer import analyze_file

issues = analyze_file("test_files/test_perfect_code.py")
assert len(issues) == 0, "Should find no issues in perfect code"

issues = analyze_file("test_files/test_parameter_issues.py")
assert len(issues) > 0, "Should find issues in problem code"

print(f"✅ Found {len(issues)} issues as expected")
```

## Common Issues and Solutions

### Issue 1: Command Not Found

```bash
$ auto-refactor-ai
bash: auto-refactor-ai: command not found
```

**Solutions:**
1. Ensure package is installed: `pip list | grep auto-refactor-ai`
2. Check scripts are installed: `which auto-refactor-ai`
3. Verify `[project.scripts]` in `pyproject.toml`
4. Reinstall: `pip install --force-reinstall .`

### Issue 2: Wrong Version Installed

```bash
$ pip show auto-refactor-ai
Version: 0.2.0  # Should be 0.3.0!
```

**Solutions:**
1. Uninstall old version: `pip uninstall auto-refactor-ai`
2. Rebuild package: `python -m build`
3. Install new version: `pip install dist/auto_refactor_ai-0.3.0-py3-none-any.whl`

### Issue 3: Module Not Found

```python
ModuleNotFoundError: No module named 'auto_refactor_ai'
```

**Solutions:**
1. Check package was installed: `pip show auto-refactor-ai`
2. Verify you're in the correct virtual environment
3. Check `[tool.setuptools.packages.find]` in `pyproject.toml`

### Issue 4: Build Fails

```bash
$ python -m build
ERROR: ...
```

**Solutions:**
1. Install build tools: `pip install --upgrade build setuptools wheel`
2. Check `pyproject.toml` syntax
3. Ensure all required files exist (README.md, LICENSE)

## Directory Structure for V3

```
auto-refactor-ai/
├── auto_refactor_ai/          # Main package
│   ├── __init__.py
│   ├── __main__.py
│   ├── analyzer.py
│   ├── cli.py
│   └── config.py
├── docs/                       # Documentation
│   ├── versions/
│   │   ├── V0_GUIDE.md
│   │   ├── V1_GUIDE.md
│   │   ├── V2_GUIDE.md
│   │   └── V3_GUIDE.md        # This file
│   └── LEARNING_GUIDE.md
├── examples/                   # Example configs
│   ├── config-strict.toml
│   └── config-relaxed.toml
├── test_files/                 # Test files (not distributed)
│   └── ...
├── dist/                       # Built packages (generated)
│   ├── *.tar.gz
│   └── *.whl
├── build/                      # Build artifacts (generated)
├── *.egg-info/                 # Package metadata (generated)
├── pyproject.toml              # Package configuration
├── LICENSE                     # MIT License
├── MANIFEST.in                 # Distribution manifest
├── README.md                   # Main documentation
└── CHANGELOG.md                # Version history
```

## Exercises

1. **Add `--version` flag**: Display package version
2. **Add entry in `README.md`**: Add installation section
3. **Create development install script**: `pip install -e .`
4. **Add badge to README**: PyPI version badge
5. **Create release checklist**: Steps for each release

## Next Steps

In V4, we'll add:
- Unit tests with pytest
- Test coverage reporting
- GitHub Actions CI/CD
- Pre-commit hooks
- Code quality checks (black, ruff)

## Key Takeaways

✅ **Console scripts** make packages user-friendly
✅ **pyproject.toml** is the modern way to configure packages
✅ **Semantic versioning** communicates changes clearly
✅ **MANIFEST.in** controls distributed files
✅ **Virtual environments** isolate testing
✅ **TestPyPI** lets you test before real release
✅ **Proper packaging** makes your tool professional

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Classifiers](https://pypi.org/classifiers/)
- [Semantic Versioning](https://semver.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
