# Auto Refactor AI

![Auto Refactor AI](https://img.shields.io/badge/auto--refactor--ai-v0.11.0-blue)

AI-powered static analyzer for Python with real-time diagnostics and refactoring suggestions.

## Features

- **Real-time Diagnostics**: See code quality issues as you type
- **Quick Fixes**: Code actions for common issues
- **Hover Information**: Detailed explanations on hover
- **Function Length**: Detect overly long functions
- **Parameter Count**: Warn about too many parameters
- **Nesting Depth**: Flag deeply nested code

## Requirements

- **Python 3.8+** with auto-refactor-ai installed:
  ```bash
  pip install auto-refactor-ai[lsp]
  ```

## Extension Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `autoRefactorAi.pythonPath` | `python` | Path to Python interpreter |
| `autoRefactorAi.maxFunctionLength` | `30` | Maximum function length |
| `autoRefactorAi.maxParameters` | `5` | Maximum parameters |
| `autoRefactorAi.maxNestingDepth` | `3` | Maximum nesting depth |

## Usage

1. Open any Python file
2. Issues appear as underlines (red=error, yellow=warning)
3. Hover over issues for explanations
4. Click the lightbulb for quick fixes

## Commands

- **Auto Refactor AI: Analyze Current File** - Manually trigger analysis

## Release Notes

### 0.11.0
- Initial release
- Real-time diagnostics
- Code actions and hover support
- LSP integration

## License

MIT
