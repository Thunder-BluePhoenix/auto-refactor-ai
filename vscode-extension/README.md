# Auto Refactor AI - VS Code Extension

This VS Code extension provides real-time code analysis for Python files using the Auto Refactor AI analyzer.

## Features

- **Real-time Diagnostics**: See code quality issues as you type
- **Quick Fixes**: Get actionable suggestions for each issue
- **Hover Information**: See detailed explanations on hover
- **Commands**: Manually trigger analysis

## Requirements

- Python 3.8+
- Auto Refactor AI package installed with LSP support:
  ```bash
  pip install auto-refactor-ai[lsp]
  ```

## Installation

### From Source

1. Clone this repository
2. Open in VS Code
3. Run `npm install`
4. Run `npm run compile`
5. Press F5 to launch Extension Development Host

### From VSIX (Coming Soon)

```bash
code --install-extension auto-refactor-ai-0.11.0.vsix
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `autoRefactorAi.pythonPath` | `python` | Path to Python interpreter |
| `autoRefactorAi.maxFunctionLength` | `30` | Maximum function length |
| `autoRefactorAi.maxParameters` | `5` | Maximum parameters |
| `autoRefactorAi.maxNestingDepth` | `3` | Maximum nesting depth |

## Usage

1. Open a Python file
2. Issues will appear as squiggly underlines
3. Hover over an issue for explanation
4. Use quick fixes (lightbulb) to see suggestions

## Commands

- `Auto Refactor AI: Analyze Current File` - Manually trigger analysis

## Development

```bash
# Install dependencies
npm install

# Compile
npm run compile

# Watch mode
npm run watch

# Package
vsce package
```

## License

MIT
