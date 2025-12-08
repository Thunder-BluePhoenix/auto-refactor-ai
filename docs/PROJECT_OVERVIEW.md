# Project Overview

Complete overview of the Auto Refactor AI project.

---

## 📁 Project Structure

```
auto-refactor-ai/
│
├── auto_refactor_ai/          # Main package
│   ├── __init__.py            # Package initialization
│   ├── __main__.py            # Module entry point
│   ├── analyzer.py            # Core analysis logic (V0-V4)
│   ├── cli.py                 # Command-line interface (V0-V6)
│   ├── config.py              # Configuration management (V2+)
│   ├── explanations.py        # Template explanations (V5)
│   ├── llm_providers.py       # LLM provider abstraction (V6)
│   └── ai_suggestions.py      # AI-powered suggestions (V6)
│
├── tests/                     # Test suite - 113 tests
│   └── test_*.py             # 6 test modules
│
├── docs/                      # Complete documentation
│   ├── README.md              # Documentation index
│   ├── ROADMAP.md            # V0-V12 development plan
│   ├── ARCHITECTURE.md       # Code structure & design
│   ├── LEARNING_GUIDE.md     # Tutorials & exercises
│   ├── API_REFERENCE.md      # Technical reference
│   ├── PROJECT_OVERVIEW.md   # This file
│   │
│   ├── versions/             # Version-specific guides
│   │   ├── V0_GUIDE.md       # V0-V6 implementation walkthrough
│   │   └── ...
│   │
│   └── learning/             # Additional learning materials
│
├── pyproject.toml            # Package metadata
├── README.md                 # Main project README
├── QUICKSTART.md            # 5-minute quick start
└── .gitignore               # Git ignore patterns
```

---

## 🎯 Project Mission

**Transform Python developers from beginner to advanced** by building a real-world static analysis tool.

**Three Goals:**

1. **Educational** - Learn Python, AST, architecture, testing, AI, and more
2. **Practical** - Build a useful tool for improving code quality
3. **Progressive** - Start simple (V0), grow complex (V1-V12)

---

## 📊 Current Status

**Version:** V8 (v0.8.0) - Project-Level Analysis ✅

**What Works:**
- ✅ Multiple analysis rules (length, parameters, nesting)
- ✅ Severity levels (INFO, WARN, CRITICAL)
- ✅ Configuration files (TOML/YAML)
- ✅ JSON output for CI/CD integration
- ✅ Pip installable package
- ✅ Comprehensive test suite (146 tests, 85%+ coverage)
- ✅ GitHub Actions CI/CD (15 combinations)
- ✅ Pre-commit hooks
- ✅ Code quality tools (black, ruff, mypy)
- ✅ Detailed explanations & best practices (V5)
- ✅ LLM-powered AI suggestions (V6)
- ✅ Support for 4 LLM providers (OpenAI, Anthropic, Google, Ollama)
- ✅ Token tracking & cost estimation
- ✅ Auto-refactor mode with `--apply` flag (V7)
- ✅ Backup system and rollback capability (V7)
- ✅ Dry-run and interactive modes (V7)
- ✅ Project-level duplicate detection (V8)
- ✅ AST hashing and architecture recommendations (V8)

**What's Next:**
- V9: Git integration & pre-commit hooks
- V10: Refactor planning mode
- ... (see [Roadmap](ROADMAP.md))

---

## 🧱 V0 Capabilities

### Features

✅ **Analyze Python Files**
- Parse Python source code
- Walk Abstract Syntax Tree (AST)
- Find all function definitions

✅ **Detect Long Functions**
- Configurable threshold (default: 30 lines)
- Accurate line counting
- Clear issue reporting

✅ **CLI Interface**
- Single file or directory
- Custom `--max-len` flag
- Clean, formatted output

✅ **Error Handling**
- Graceful syntax error handling
- File not found messages
- UTF-8 encoding support

### Example Output

```bash
$ python -m auto_refactor_ai sample_test.py

[LONG FUNCTION] sample_test.py:11-58
  - Function : very_long_function
  - Length   : 48 lines
  - Suggestion: Function 'very_long_function' in sample_test.py is 48 lines long.
                Consider splitting it into smaller functions with single responsibilities.
```

---

## 🎓 Learning Objectives

By building this project through V0-V12, you'll learn:

### Technical Skills

**V0-V4 (Fundamentals):**
- Python AST manipulation
- CLI tool development
- Package structure
- Configuration management
- Unit testing & integration testing
- CI/CD with GitHub Actions

**V5-V9 (Intermediate):**
- LLM API integration
- Prompt engineering
- Code transformation
- Diff generation
- Git integration
- Performance optimization

**V10-V12 (Advanced):**
- Project-level analysis
- Language Server Protocol (LSP)
- VS Code extension development
- Open source community building
- Documentation & marketing

### Software Engineering

- **Architecture:** Plugin systems, rule patterns, provider abstractions
- **Testing:** TDD, fixtures, mocking, coverage
- **DevOps:** CI/CD, pre-commit hooks, automation
- **Security:** Safe code transformation, validation
- **UX:** Error messages, CLI design, IDE integration

---

## 📖 Documentation Map

### For Users

| Need | Document |
|------|----------|
| Get started quickly | [QUICKSTART.md](../QUICKSTART.md) |
| Understand features | [README.md](../README.md) |
| See what's planned | [ROADMAP.md](ROADMAP.md) |

### For Developers

| Need | Document |
|------|----------|
| Build from scratch | [V0_GUIDE.md](versions/V0_GUIDE.md) |
| Understand code | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Look up functions | [API_REFERENCE.md](API_REFERENCE.md) |
| Add features | [ROADMAP.md](ROADMAP.md) |

### For Learners

| Need | Document |
|------|----------|
| Learn AST basics | [LEARNING_GUIDE.md](LEARNING_GUIDE.md) |
| Exercises | [LEARNING_GUIDE.md](LEARNING_GUIDE.md) |
| Step-by-step tutorial | [V0_GUIDE.md](versions/V0_GUIDE.md) |
| Concepts explained | [ARCHITECTURE.md](ARCHITECTURE.md) |

---

## 🔄 Development Workflow

### Typical V0 Usage

```bash
# 1. Clone/download project
cd auto-refactor-ai

# 2. Test it works
python -m auto_refactor_ai sample_test.py

# 3. Analyze your code
python -m auto_refactor_ai ~/my-project

# 4. Adjust threshold
python -m auto_refactor_ai ~/my-project --max-len 20
```

### Extending to V1

```bash
# 1. Read the roadmap
cat docs/ROADMAP.md

# 2. Create rules module
mkdir auto_refactor_ai/rules

# 3. Implement new rules
# - TooManyParametersRule
# - DeepNestingRule
# - CyclomaticComplexityRule

# 4. Update CLI to use rules

# 5. Test
python -m auto_refactor_ai . --rules all

# 6. Update documentation
```

---

## 🚀 Roadmap Summary

| Version | Focus | Complexity | Status |
|---------|-------|------------|--------|
| **V0** | Single rule analyzer | ⭐ | ✅ Complete |
| **V1** | Multiple rules | ⭐⭐ | ✅ Complete |
| **V2** | Config & JSON | ⭐⭐ | ✅ Complete |
| **V3** | Pip package | ⭐⭐ | ✅ Complete |
| **V4** | Tests & CI | ⭐⭐⭐ | ✅ Complete |
| **V5** | Explanations | ⭐⭐ | ✅ Complete |
| **V6** | LLM integration | ⭐⭐⭐⭐ | ✅ Complete |
| **V7** | Auto-fix | ⭐⭐⭐⭐ | ✅ Complete |
| **V8** | Project analysis | ⭐⭐⭐⭐ | ✅ Complete |
| **V9** | Git integration | ⭐⭐⭐ | 🔄 Next Up |
| **V10** | Planning mode | ⭐⭐⭐⭐ | 📋 Planned |
| **V11** | IDE integration | ⭐⭐⭐⭐⭐ | 📋 Planned |
| **V12** | Community launch | ⭐⭐⭐ | 📋 Planned |

Full details: [ROADMAP.md](ROADMAP.md)

---

## 🔑 Key Design Decisions

### V0 Choices

**1. AST over Regex**
- **Why:** Accurate, semantic analysis
- **Benefit:** Handles all Python syntax correctly
- **Tradeoff:** Requires valid Python (not just text)

**2. Dataclasses for Issues**
- **Why:** Type-safe, clean data structures
- **Benefit:** Easy to serialize (V2 JSON output)
- **Tradeoff:** Requires Python 3.7+

**3. Simple CLI with argparse**
- **Why:** Standard library, no dependencies
- **Benefit:** Easy to understand and extend
- **Tradeoff:** Less powerful than click/typer (can migrate in V3)

**4. No External Dependencies**
- **Why:** Beginner-friendly, easy setup
- **Benefit:** Works anywhere Python runs
- **Tradeoff:** Limited functionality (for now)

### Future Choices (V1+)

**Rule-Based Architecture (V1):**
- Plugin system for extensibility
- Each rule is independent
- Easy to add/remove/configure

**Config Files (V2):**
- TOML for simplicity
- Per-project customization
- IDE integration friendly

**LLM Provider Abstraction (V6):**
- Support multiple providers (OpenAI, Anthropic, local)
- Async for performance
- Cost tracking

---

## 📈 Metrics & Goals

### V0 Success Metrics

✅ **Functional:**
- Analyzes Python files without crashing
- Finds functions > threshold
- Handles syntax errors gracefully

✅ **Educational:**
- Code is readable and well-commented
- Documentation is comprehensive
- Learners can understand and extend it

✅ **Foundation:**
- Architecture supports future versions
- No major refactoring needed for V1
- Patterns are consistent

### V12 Success Metrics (Future)

**User Adoption:**
- 1000+ stars on GitHub
- 100+ PyPI downloads/month
- Active community discussions

**Feature Completeness:**
- 10+ analysis rules
- LLM integration
- IDE extension
- Pre-commit hook

**Learning Impact:**
- 10+ contributors
- Tutorial blog posts
- Video walkthroughs
- Classroom adoption

---

## 🤝 Contributing

### Ways to Help

**1. Use It**
- Try on your projects
- Report bugs
- Suggest features

**2. Build It**
- Implement V1, V2, etc.
- Add new rules
- Improve performance

**3. Document It**
- Write tutorials
- Create examples
- Record videos

**4. Share It**
- Blog posts
- Social media
- Presentations

### Getting Started

1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Pick a task from [ROADMAP.md](ROADMAP.md)
3. Create a branch
4. Implement & test
5. Update documentation
6. Submit pull request

---

## 📚 Resources

### Project Resources

- [Main README](../README.md)
- [Quick Start](../QUICKSTART.md)
- [Documentation Index](README.md)
- [Roadmap](ROADMAP.md)

### External Resources

- [Python AST Docs](https://docs.python.org/3/library/ast.html)
- [Green Tree Snakes](https://greentreesnakes.readthedocs.io/)
- [Refactoring Catalog](https://refactoring.guru/)
- [Python Packaging](https://packaging.python.org/)

---

## 🎯 Next Steps

**If you're new:**
1. Run the quick start
2. Read [V0_GUIDE.md](versions/V0_GUIDE.md)
3. Do exercises in [LEARNING_GUIDE.md](LEARNING_GUIDE.md)

**If you're ready to build:**
1. Study [ARCHITECTURE.md](ARCHITECTURE.md)
2. Check [ROADMAP.md](ROADMAP.md) for V1 tasks
3. Start implementing!

**If you want to contribute:**
1. Open an issue to discuss your idea
2. Fork the repository
3. Implement and document
4. Submit pull request

---

## ❓ FAQ

**Q: Why build this instead of using pylint/flake8?**

A: This is a *learning project*. The goal is to understand how static analyzers work, not to replace existing tools.

**Q: Can I use this in production?**

A: V0 is basic. Wait for V3-V4 (tests, CI, pip package) for production use.

**Q: How long does each version take?**

A: 3-7 days of focused work, but go at your own pace!

**Q: Do I need AI/LLM experience?**

A: Not for V0-V5. LLM integration starts in V6.

**Q: What if I get stuck?**

A: Check documentation, open an issue, or ask in discussions!

---

**Ready to start?**

👉 [Quick Start Guide](../QUICKSTART.md)

👉 [V0 Implementation Guide](versions/V0_GUIDE.md)

👉 [Full Documentation](README.md)
