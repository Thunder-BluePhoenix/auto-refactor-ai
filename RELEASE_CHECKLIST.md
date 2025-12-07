# Release Checklist

Use this checklist before each release to ensure quality and consistency.

## Pre-Release (Development)

### Code Quality
- [ ] All features implemented and working
- [ ] No known critical bugs
- [ ] Code follows project style guidelines
- [ ] No TODO comments in production code
- [ ] All debug print statements removed

### Testing
- [ ] All existing tests pass
- [ ] New features have tests
- [ ] Manual testing completed
- [ ] Tested on multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
- [ ] Tested on different OS (Windows, macOS, Linux)
- [ ] Edge cases tested

### Documentation
- [ ] `README.md` updated with new features
- [ ] `CHANGELOG.md` updated with changes
- [ ] Version number updated in `pyproject.toml`
- [ ] API documentation updated (if applicable)
- [ ] Examples updated
- [ ] Docstrings complete and accurate

### Package Files
- [ ] `pyproject.toml` version bumped
- [ ] `LICENSE` file present
- [ ] `MANIFEST.in` includes all necessary files
- [ ] `.gitignore` excludes build artifacts
- [ ] No sensitive data in repository

## Build & Verify

### Clean Build
- [ ] Remove old build artifacts:
  ```bash
  rm -rf dist/ build/ *.egg-info/
  ```
- [ ] Build fresh package:
  ```bash
  python -m build
  ```
- [ ] Verify build completed successfully

### Package Verification
- [ ] Run twine check:
  ```bash
  twine check dist/*
  ```
- [ ] All files pass validation
- [ ] No errors or warnings

### Local Installation Test
- [ ] Install in fresh virtual environment:
  ```bash
  python -m venv test_env
  source test_env/bin/activate  # Windows: test_env\Scripts\activate
  pip install dist/*.whl
  ```
- [ ] Run verification script:
  ```bash
  python scripts/verify_install.py
  ```
- [ ] All tests pass (6/6)
- [ ] Clean up:
  ```bash
  deactivate
  rm -rf test_env
  ```

### Command Testing
- [ ] `auto-refactor-ai --help` works
- [ ] `auto-refactor-ai test_files/` works
- [ ] `auto-refactor-ai --format json` works
- [ ] `auto-refactor-ai --config examples/config-strict.toml` works
- [ ] All CLI flags function correctly

## TestPyPI Upload

### Upload to TestPyPI
- [ ] Upload package:
  ```bash
  twine upload --repository testpypi dist/*
  ```
- [ ] Upload successful (no errors)
- [ ] Note the TestPyPI URL

### TestPyPI Installation
- [ ] Create fresh environment
- [ ] Install from TestPyPI:
  ```bash
  pip install --index-url https://test.pypi.org/simple/ auto-refactor-ai
  ```
- [ ] Run tests again
- [ ] Verify everything works
- [ ] Clean up environment

### TestPyPI Page
- [ ] Visit TestPyPI project page
- [ ] README renders correctly
- [ ] Metadata is accurate
- [ ] Links work
- [ ] Version number is correct

## PyPI Upload (Production)

### Final Checks
- [ ] TestPyPI installation successful
- [ ] All tests passed on TestPyPI version
- [ ] Ready to make public
- [ ] Team/maintainers notified (if applicable)

### Upload to PyPI
- [ ] Upload package:
  ```bash
  twine upload dist/*
  ```
- [ ] Upload successful
- [ ] Note the PyPI URL

### PyPI Installation
- [ ] Create fresh environment
- [ ] Install from PyPI:
  ```bash
  pip install auto-refactor-ai
  ```
- [ ] Run comprehensive tests
- [ ] Verify all features work
- [ ] Test on different machines (if possible)

### PyPI Page
- [ ] Visit https://pypi.org/project/auto-refactor-ai/
- [ ] README renders correctly
- [ ] All metadata accurate
- [ ] Links functional
- [ ] Version correct
- [ ] Classifiers appropriate

## Post-Release

### Git & GitHub
- [ ] Commit all changes:
  ```bash
  git add .
  git commit -m "Release v0.3.0"
  ```
- [ ] Create git tag:
  ```bash
  git tag -a v0.3.0 -m "Version 0.3.0 - Pip Installable Package"
  ```
- [ ] Push commits and tags:
  ```bash
  git push origin main
  git push origin v0.3.0
  ```

### GitHub Release
- [ ] Go to GitHub releases
- [ ] Click "Create a new release"
- [ ] Select tag `v0.3.0`
- [ ] Title: "V3 - Pip Installable Package"
- [ ] Description from CHANGELOG
- [ ] Attach `dist/*.whl` file
- [ ] Attach `dist/*.tar.gz` file
- [ ] Publish release

### Documentation
- [ ] Update main `README.md` installation section
- [ ] Update docs if needed
- [ ] Verify documentation site (if applicable)
- [ ] Update examples if needed

### Communication
- [ ] Update project status in README
- [ ] Announce on social media (optional):
  - [ ] Twitter/X
  - [ ] Reddit (r/Python)
  - [ ] LinkedIn
  - [ ] Dev.to
  - [ ] Blog post
- [ ] Notify users/contributors
- [ ] Update project homepage

### Monitoring
- [ ] Check PyPI stats: https://pypistats.org/packages/auto-refactor-ai
- [ ] Monitor for issues
- [ ] Watch GitHub for new issues/PRs
- [ ] Respond to community feedback

## Version-Specific Checklists

### V3 (Current - 0.3.0)
- [x] Pip installable package
- [x] Console script entry point
- [x] Proper packaging setup
- [x] Documentation guides
- [x] Verification script

### V4 (Next - 0.4.0)
- [ ] pytest test suite
- [ ] Test coverage >80%
- [ ] GitHub Actions CI/CD
- [ ] Pre-commit hooks
- [ ] Code quality checks (black, ruff)

## Common Issues

### Upload fails with "File already exists"
**Solution:** Bump version number in `pyproject.toml` and rebuild

### README doesn't render on PyPI
**Solution:** Check Markdown syntax, test on GitHub first

### Package missing files
**Solution:** Update `MANIFEST.in` and rebuild

### Import errors after install
**Solution:** Check `pyproject.toml` package discovery settings

### Command not found after install
**Solution:** Verify `[project.scripts]` entry point is correct

## Quick Reference

### Version Bumping
```toml
# pyproject.toml
version = "0.3.0"  # Major.Minor.Patch
```

### Rebuild Command
```bash
rm -rf dist/ build/ *.egg-info/ && python -m build
```

### Upload Commands
```bash
# TestPyPI
twine upload --repository testpypi dist/*

# PyPI
twine upload dist/*
```

### Install Commands
```bash
# From TestPyPI
pip install --index-url https://test.pypi.org/simple/ auto-refactor-ai

# From PyPI
pip install auto-refactor-ai

# From local wheel
pip install dist/*.whl

# Development mode
pip install -e .
```

## Notes

- Always test on TestPyPI first
- Keep tokens secure
- Version numbers can't be reused
- PyPI uploads are permanent
- Coordinate with team before major releases
