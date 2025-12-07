# Quick Start Guide

Welcome to Auto Refactor AI V0! Let's get you up and running in less than 5 minutes.

## Step 1: Verify Python Installation

Make sure you have Python 3.8 or higher:

```bash
python --version
```

## Step 2: Navigate to the Project

```bash
cd auto-refactor-ai
```

## Step 3: (Optional) Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

## Step 4: Test It Out!

Try analyzing the included sample file:

```bash
python -m auto_refactor_ai sample_test.py
```

You should see output like:

```
[LONG FUNCTION] sample_test.py:11-58
  - Function : very_long_function
  - Length   : 48 lines
  - Suggestion: Function 'very_long_function' in sample_test.py is 48 lines long...
```

## Step 5: Analyze Your Own Code

Point it at any Python file or directory:

```bash
# Single file
python -m auto_refactor_ai path/to/your_file.py

# Entire project
python -m auto_refactor_ai path/to/your_project

# Current directory
python -m auto_refactor_ai .
```

## Step 6: Customize the Threshold

The default threshold is 30 lines. Adjust it with `--max-len`:

```bash
python -m auto_refactor_ai . --max-len 20
```

## What's Next?

Now that V0 is working, here's how you can evolve this project:

### V1: Add More Rules
- Detect high cyclomatic complexity
- Find deeply nested code
- Identify too many parameters
- Spot duplicate code patterns

### V2: Better Reporting
- Generate HTML reports
- Export to JSON/CSV
- Show code context
- Add severity levels

### V3: AI Integration
- Use LLMs to suggest specific refactorings
- Generate refactored code examples
- Explain why refactoring is needed

### V4: Auto-Fix Mode
- Automatically apply simple refactorings
- Interactive fix mode
- Git integration for safe changes

## Learning Resources

- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [Code Smells and Refactoring](https://refactoring.guru/refactoring/smells)
- [Static Analysis Principles](https://en.wikipedia.org/wiki/Static_program_analysis)

## Got Questions?

- Check out [README.md](README.md) for detailed documentation
- Look at the code in `auto_refactor_ai/` - it's simple and well-commented
- Experiment! Try breaking things and see what happens

Happy refactoring!
