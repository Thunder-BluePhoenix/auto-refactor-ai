# Contributing to Auto Refactor AI

Thank you for your interest in contributing! We welcome all contributions, from bug reports to new features.

## 🚀 Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/auto-refactor-ai.git
   cd auto-refactor-ai
   ```
3. **Install dependencies**:
   ```bash
   pip install -e ".[dev,lsp,ai-all]"
   ```
4. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/amazing-feature
   ```

## 🛠 Development Workflow

### Running Tests
We use `pytest` for testing. Ensure all tests pass before submitting.

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_project_analyzer.py
```

### Linting and Formatting
We use `ruff` and `black`.

```bash
# Check linting
ruff check .

# Format code
black .
```

### VS Code Extension
If modifying the extension:
```bash
cd vscode-extension
npm install
npm run compile
```

## 📝 Pull Request Guidelines

1. **Keep it small**: Smaller PRs are easier to review.
2. **Add tests**: New features should have tests.
3. **Update docs**: Update README or docstrings if needed.
4. **Use descriptive titles**: "Fix infinite loop in analyzer" instead of "Fix bug".

## 🐛 Reporting Bugs

Open an issue using the **Bug Report** template. Include:
- Version used
- Minimal code example
- Expected vs actual behavior

## 💡 Feature Requests

Open an issue using the **Feature Request** template. Describe:
- The problem you're solving
- Your proposed solution
- Alternative approaches

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
