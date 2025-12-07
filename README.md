# Auto Refactor AI - V0

A beginner-friendly static analyzer that detects long functions in Python code and suggests refactoring opportunities.

## What is V0?

V0 is the foundational version of Auto Refactor AI. It focuses on a single, simple rule:

**Scan Python files → Detect long functions → Print refactor suggestions**

No AI, no complexity. Just clean, simple static analysis that works.

## Features

- Analyzes single Python files or entire directories
- Detects functions that exceed a configurable line length threshold
- Provides clear, actionable refactoring suggestions
- Fast and lightweight - no external dependencies

## Installation

1. Clone or download this project
2. Navigate to the project directory
3. (Optional) Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

## Usage

### Analyze a single file

```bash
python -m auto_refactor_ai path/to/your_script.py
```

### Analyze an entire directory

```bash
python -m auto_refactor_ai .
```

### Custom function length threshold

By default, functions longer than 30 lines are flagged. You can customize this:

```bash
python -m auto_refactor_ai . --max-len 20
```

## Example Output

```
[LONG FUNCTION] my_app/utils.py:10-75
  - Function : process_data
  - Length   : 66 lines
  - Suggestion: Function 'process_data' in my_app/utils.py is 66 lines long. Consider splitting it into smaller functions with single responsibilities.
```

## Project Structure

```
auto-refactor-ai/
│
├─ auto_refactor_ai/
│   ├─ __init__.py      # Package initialization
│   ├─ analyzer.py      # Core analysis logic
│   └─ cli.py           # Command line interface
│
├─ pyproject.toml       # Package metadata
└─ README.md            # This file
```

## How It Works

1. **Read** - Loads the Python source code
2. **Parse** - Uses Python's `ast` module to build an Abstract Syntax Tree
3. **Analyze** - Walks the AST to find function definitions
4. **Report** - Flags functions exceeding the line length threshold

## Roadmap

V0 is just the beginning. Future versions will include:

- **V1**: Multiple analysis rules (complexity, nesting depth, etc.)
- **V2**: Config files & JSON output
- **V3**: Pip installable package
- **V4**: Tests & CI/CD
- **V5**: Detailed explanations
- **V6**: AI-powered suggestions using LLMs
- **V7**: Auto-fix mode with automated refactoring
- **V8**: Project-level analysis
- **V9**: Git integration & pre-commit hooks
- **V10**: Refactor planning mode
- **V11**: Editor/IDE integration
- **V12**: Community-ready release

See the complete [Roadmap](docs/ROADMAP.md) for detailed plans.

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

- **[Roadmap](docs/ROADMAP.md)** - Complete version-by-version plan (V0-V12)
- **[Architecture Guide](docs/ARCHITECTURE.md)** - How the code works internally
- **[Learning Guide](docs/LEARNING_GUIDE.md)** - Educational tutorials and exercises
- **[API Reference](docs/API_REFERENCE.md)** - Complete code documentation
- **[V0 Implementation Guide](docs/versions/V0_GUIDE.md)** - Step-by-step V0 walkthrough

## Learning Path

This project is designed to teach you Python development:

**Beginner Track (V0-V4):**
- V0: Python AST basics, CLI tools
- V1: Software architecture, rule systems
- V2: Configuration management, data formats
- V3: Python packaging & distribution
- V4: Testing, CI/CD, code quality

**Intermediate Track (V5-V9):**
- V5-V6: LLM integration, prompt engineering
- V7: Code transformation & safety
- V8-V9: Advanced AST, Git integration

**Advanced Track (V10-V12):**
- V10: Strategic analysis & planning
- V11: Editor tooling, LSP
- V12: Open source community building

## Contributing

This is a learning project designed to help developers grow from beginner to advanced. Contributions, suggestions, and improvements are welcome!

**Ways to contribute:**
- Implement features from the roadmap
- Add new analysis rules
- Improve documentation
- Create tutorials or examples
- Report bugs or suggest features

See [CONTRIBUTING.md](CONTRIBUTING.md) (coming in V12) for guidelines.

## License

MIT License - Feel free to use this project for learning and experimentation.
