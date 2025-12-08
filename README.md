# Auto Refactor AI 🔧

<p align="center">
  <img src="https://img.shields.io/badge/version-0.12.0-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License">
</p>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/yourusername/auto-refactor-ai/test.yml?label=tests&style=flat-square" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-87%25-brightgreen?style=flat-square" alt="Coverage">
  <img src="https://img.shields.io/badge/tests-299%20passed-brightgreen?style=flat-square" alt="299 Tests">
</p>

<p align="center">
  <b>AI-powered Python code analyzer with refactoring suggestions, LSP support, and VS Code integration.</b>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Static Analysis** | Detect long functions, deep nesting, too many parameters |
| 🤖 **AI Suggestions** | LLM-powered refactoring recommendations |
| 📊 **Refactor Plans** | Strategic roadmaps with priority ranking |
| 🎯 **VS Code Extension** | Real-time diagnostics as you type |
| 🔌 **LSP Server** | Works with any editor (Neovim, Emacs) |
| 🔄 **Auto-Apply** | Automatic refactoring with backup |
| 📁 **Project Analysis** | Duplicate code detection |
| 🌿 **Git Integration** | Analyze staged/modified files |

---

## 🚀 Quick Start

```bash
# Install
pip install auto-refactor-ai

# Analyze your code
auto-refactor-ai .

# With AI suggestions
auto-refactor-ai . --ai-suggestions

# Generate refactor plan
auto-refactor-ai . --plan --plan-format html -o report.html

# Start LSP server for editor integration
auto-refactor-ai --lsp
```

---

## 📦 Installation

```bash
# Basic install
pip install auto-refactor-ai

# With LSP support (for VS Code/Neovim)
pip install auto-refactor-ai[lsp]

# With AI features
pip install auto-refactor-ai[ai-all]

# Everything
pip install auto-refactor-ai[lsp,ai-all,dev]
```

---

## 🔧 Usage Examples

### Analyze a Directory

```bash
auto-refactor-ai src/
```

**Output:**
```
[CRITICAL] src/service.py:26-92  process_order()
  - Function is 67 lines long (max: 30)

[WARN] src/utils.py:14-23  validate_data()
  - 5 levels of nesting (max: 3)

============================================================
SUMMARY: CRITICAL: 1, WARN: 4, INFO: 8, TOTAL: 13
============================================================
```

### Generate Refactor Plan

```bash
auto-refactor-ai . --plan --plan-format html -o report.html
```

Creates a styled HTML report with:
- Executive summary
- Critical hotspots
- Quick wins
- Strategic roadmap

### VS Code Integration

1. Install the VS Code extension from `vscode-extension/`
2. Open Python files
3. See issues as underlines, hover for explanations

---

## ⚙️ Configuration

Create `.auto-refactor-ai.toml`:

```toml
max_function_length = 30
max_parameters = 5
max_nesting_depth = 3
enabled_rules = ["function-too-long", "too-many-parameters", "deep-nesting"]
```

Or use `pyproject.toml`:

```toml
[tool.auto-refactor-ai]
max_function_length = 25
max_parameters = 4
```

---

## 📋 CLI Reference

| Flag | Description |
|------|-------------|
| `--format json` | JSON output |
| `--explain` | Detailed explanations |
| `--ai-suggestions` | AI recommendations |
| `--plan` | Generate refactor plan |
| `--apply` | Auto-apply fixes |
| `--git` | Analyze modified files |
| `--staged` | Analyze staged files |
| `--lsp` | Start language server |

---

## 🧪 Version History

| Version | Highlights |
|---------|------------|
| **V12** | Community-ready release, examples, templates |
| **V11** | LSP server, VS Code extension |
| **V10** | Refactor planning, HTML reports |
| **V9** | Git integration |
| **V8** | Project-level duplicate detection |
| **V7** | Auto-apply mode |
| **V6** | AI/LLM integration |

See [CHANGELOG.md](CHANGELOG.md) for full history.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick ways to contribute:**
- 🐛 Report bugs
- 💡 Suggest features
- 📖 Improve docs
- 🔧 Submit PRs

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

<p align="center">
  Made with ❤️ for clean Python code
</p>
