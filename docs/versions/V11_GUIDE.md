# V11 Implementation Guide: IDE/Editor Integration

## Overview

V11 adds Language Server Protocol (LSP) support, enabling real-time code analysis in any LSP-compatible editor.

## Goals

1. Create an LSP server using `pygls`
2. Provide real-time diagnostics
3. Implement code actions (quick fixes)
4. Add hover information
5. Create VS Code extension

## New CLI Flags (V11)

| Flag | Description | Default |
|------|-------------|---------|
| `--lsp` | Start LSP server | False |
| `--lsp-tcp` | Use TCP transport | False (stdio) |
| `--lsp-port` | TCP port | 2087 |

## Installation

```bash
# Install with LSP support
pip install auto-refactor-ai[lsp]
```

## Usage

### With VS Code

1. Install the extension from `vscode-extension/`
2. Open a Python file
3. Issues appear as underlines automatically

### With Neovim

```lua
-- In your LSP config
require('lspconfig').auto_refactor_ai.setup{
  cmd = {"auto-refactor-ai", "--lsp"},
  filetypes = {"python"},
}
```

### Standalone Server

```bash
# Start in stdio mode (default)
auto-refactor-ai --lsp

# Start in TCP mode for debugging
auto-refactor-ai --lsp --lsp-tcp --lsp-port 2087
```

## Architecture

### LSP Server (`lsp_server.py`)

```python
from pygls.lsp.server import LanguageServer

class AutoRefactorLanguageServer(LanguageServer):
    def get_diagnostics(uri, content) -> List[Diagnostic]
    def _issue_to_diagnostic(issue) -> Diagnostic

# Feature handlers
@server.feature(TEXT_DOCUMENT_DID_OPEN)
@server.feature(TEXT_DOCUMENT_DID_SAVE)
@server.feature(TEXT_DOCUMENT_CODE_ACTION)
@server.feature(TEXT_DOCUMENT_HOVER)
```

### VS Code Extension

```
vscode-extension/
├── package.json          # Extension manifest
├── tsconfig.json         # TypeScript config
├── src/extension.ts      # Language client
└── README.md             # Setup guide
```

## Testing

```bash
# Run V11 tests
pytest tests/test_lsp_server.py -v

# All tests
pytest tests/ -v --no-cov
```

---

**V11 Status:** ✅ COMPLETE
**Next:** V12 - Community-Ready Release
