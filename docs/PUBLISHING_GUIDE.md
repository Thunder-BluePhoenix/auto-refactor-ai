# Publishing to PyPI - Complete Guide

This guide walks you through publishing `auto-refactor-ai` to PyPI (Python Package Index), making it available for anyone to install with `pip install auto-refactor-ai`.

## Prerequisites

- [x] Package is built and tested locally
- [x] All verification tests pass
- [x] Version number is updated in `pyproject.toml`
- [x] `CHANGELOG.md` is updated
- [x] `README.md` is complete and accurate
- [x] LICENSE file exists

## Step-by-Step Guide

### Step 1: Create PyPI Accounts

You need accounts on both TestPyPI (for testing) and PyPI (for production).

#### 1.1 Create TestPyPI Account

1. Go to https://test.pypi.org/account/register/
2. Fill in your details
3. Verify your email
4. Enable 2FA (recommended)

#### 1.2 Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Fill in your details
3. Verify your email
4. Enable 2FA (required for new projects)

#### 1.3 Create API Tokens

For security, use API tokens instead of passwords.

**For TestPyPI:**
1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "auto-refactor-ai-test"
4. Scope: "Entire account" (or limit to project after first upload)
5. Copy the token (starts with `pypi-`)
6. Save it securely - you can't see it again!

**For PyPI:**
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "auto-refactor-ai"
4. Scope: "Entire account" (or limit to project after first upload)
5. Copy the token
6. Save it securely!

### Step 2: Install Twine

Twine is the official tool for uploading packages to PyPI.

```bash
pip install --upgrade twine
```

### Step 3: Build the Package

Clean previous builds and create fresh distributions:

```bash
# Remove old builds
rm -rf dist/ build/ *.egg-info/

# Build fresh distributions
python -m build
```

This creates:
- `dist/auto_refactor_ai-0.3.0-py3-none-any.whl` (wheel)
- `dist/auto_refactor_ai-0.3.0.tar.gz` (source)

### Step 4: Check the Distribution

Verify the package is properly formatted:

```bash
twine check dist/*
```

Expected output:
```
Checking dist/auto_refactor_ai-0.3.0-py3-none-any.whl: PASSED
Checking dist/auto_refactor_ai-0.3.0.tar.gz: PASSED
```

### Step 5: Upload to TestPyPI (Recommended First)

Test the upload process on TestPyPI first:

```bash
twine upload --repository testpypi dist/*
```

You'll be prompted:
```
Enter your username: __token__
Enter your password: <paste your TestPyPI token>
```

**Note:** Username is literally `__token__` (with double underscores)

Expected output:
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading auto_refactor_ai-0.3.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 15.2/15.2 kB
Uploading auto_refactor_ai-0.3.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 20.1/20.1 kB

View at:
https://test.pypi.org/project/auto-refactor-ai/0.3.0/
```

### Step 6: Test Installation from TestPyPI

Create a fresh virtual environment and test:

```bash
# Create test environment
python -m venv test_pypi_env
source test_pypi_env/bin/activate  # On Windows: test_pypi_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ auto-refactor-ai

# Test it works
auto-refactor-ai --help
auto-refactor-ai test_files/test_perfect_code.py

# Clean up
deactivate
rm -rf test_pypi_env
```

### Step 7: Upload to PyPI (Production)

Once TestPyPI works, upload to real PyPI:

```bash
twine upload dist/*
```

You'll be prompted:
```
Enter your username: __token__
Enter your password: <paste your PyPI token>
```

Expected output:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading auto_refactor_ai-0.3.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 15.2/15.2 kB
Uploading auto_refactor_ai-0.3.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 20.1/20.1 kB

View at:
https://pypi.org/project/auto-refactor-ai/0.3.0/
```

### Step 8: Verify on PyPI

1. Visit https://pypi.org/project/auto-refactor-ai/
2. Check the page looks correct
3. Verify README renders properly
4. Check metadata is accurate

### Step 9: Test Public Installation

```bash
# Create fresh environment
python -m venv test_real_env
source test_real_env/bin/activate

# Install from PyPI (this is what users will run!)
pip install auto-refactor-ai

# Test it
auto-refactor-ai --help
auto-refactor-ai --version  # If you added this

# Clean up
deactivate
rm -rf test_real_env
```

### Step 10: Create GitHub Release (Optional)

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag: `v0.3.0`
4. Title: "V3 - Pip Installable Package"
5. Description: Copy from CHANGELOG.md
6. Attach distribution files (wheel + tar.gz)
7. Publish release

## Using .pypirc for Easier Uploads

Create `~/.pypirc` to store configuration:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <your PyPI token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your TestPyPI token>
```

**Security Note:** Keep this file secure! Use `chmod 600 ~/.pypirc` on Unix.

Now you can upload without entering credentials:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Troubleshooting

### Error: "File already exists"

PyPI doesn't allow re-uploading the same version. Solutions:

1. **Recommended:** Bump the version number
   ```toml
   # pyproject.toml
   version = "0.3.1"  # Increment patch version
   ```

2. Delete from TestPyPI (only works there, not PyPI!)
   - Go to project settings
   - Delete the version
   - Re-upload

### Error: "Invalid or non-existent authentication"

- Double-check your token
- Username must be `__token__` (literal string)
- Token should start with `pypi-`
- Make sure you're using the right token (TestPyPI vs PyPI)

### Error: "403 Forbidden"

- You don't have permission for this project name
- Someone else owns it
- Try a different name in `pyproject.toml`

### README not rendering

- Make sure `readme = "README.md"` in `pyproject.toml`
- Check README is valid Markdown
- Try viewing on GitHub first

### Missing files in package

- Check `MANIFEST.in`
- Verify with: `tar -tzf dist/*.tar.gz | less`
- Make sure files are in `include` directives

## Release Checklist

Use this checklist for each release:

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md`
- [ ] Update `README.md` if needed
- [ ] Run all tests locally
- [ ] Build package: `python -m build`
- [ ] Check package: `twine check dist/*`
- [ ] Upload to TestPyPI
- [ ] Test install from TestPyPI
- [ ] Upload to PyPI
- [ ] Test install from PyPI
- [ ] Create GitHub release
- [ ] Update documentation
- [ ] Announce on social media (optional)

## Version Numbering

Follow semantic versioning (semver.org):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
  - **MAJOR**: Breaking changes (1.0.0 → 2.0.0)
  - **MINOR**: New features, backward compatible (1.0.0 → 1.1.0)
  - **PATCH**: Bug fixes (1.0.0 → 1.0.1)

For our project:
- `0.3.0` - V3 (current)
- `0.4.0` - V4 (next - tests & CI/CD)
- `0.5.0` - V5 (detailed explanations)
- `1.0.0` - First stable release

## Updating an Existing Package

When releasing a new version:

1. **Make changes** to code
2. **Update version** in `pyproject.toml`
3. **Update CHANGELOG.md**
4. **Rebuild**:
   ```bash
   rm -rf dist/ build/ *.egg-info/
   python -m build
   ```
5. **Upload**:
   ```bash
   twine upload dist/*
   ```

## Security Best Practices

1. **Use API tokens**, not passwords
2. **Enable 2FA** on PyPI account
3. **Keep .pypirc secure** (chmod 600)
4. **Don't commit tokens** to git
5. **Use scoped tokens** (limit to one project)
6. **Rotate tokens** periodically
7. **Use different tokens** for TestPyPI and PyPI

## Marketing Your Package

Once published:

1. **Add PyPI badge** to README:
   ```markdown
   [![PyPI version](https://badge.fury.io/py/auto-refactor-ai.svg)](https://badge.fury.io/py/auto-refactor-ai)
   ```

2. **Share on social media**:
   - Twitter/X
   - Reddit (r/Python, r/learnpython)
   - LinkedIn
   - Dev.to
   - Hacker News

3. **Submit to awesome lists**:
   - awesome-python
   - awesome-static-analysis

4. **Write blog post** explaining the tool

## Useful Commands

```bash
# View package info
pip show auto-refactor-ai

# List files in package
pip show -f auto-refactor-ai

# Check what's in the wheel
unzip -l dist/*.whl

# Check what's in the tarball
tar -tzf dist/*.tar.gz

# Verify package can be installed
pip install dist/*.whl --dry-run
```

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
- [PyPI Classifiers](https://pypi.org/classifiers/)

## Next Steps

After publishing:
- Monitor downloads: https://pypistats.org/packages/auto-refactor-ai
- Respond to issues on GitHub
- Plan next version (V4 - Tests & CI/CD!)
- Keep improving based on user feedback
