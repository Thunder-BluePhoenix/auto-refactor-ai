"""Language Server Protocol implementation for Auto Refactor AI (V11).

This module provides an LSP server using pygls that integrates with
any LSP-compatible editor (VS Code, Neovim, Emacs, etc.).

Features:
- Real-time diagnostics as you type
- Code actions for quick fixes
- Hover information for issue explanations
"""

import logging
from typing import List, Optional

# LSP imports - wrapped for optional dependency
try:
    from lsprotocol import types as lsp
    from pygls.lsp.server import LanguageServer

    HAS_PYGLS = True
except ImportError:
    HAS_PYGLS = False
    LanguageServer = object  # type: ignore
    lsp = None  # type: ignore

from .analyzer import Issue, Severity, analyze_file
from .config import load_config
from .explanations import get_explanation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server name and version
SERVER_NAME = "auto-refactor-ai"
SERVER_VERSION = "0.11.0"


def check_pygls_available():
    """Check if pygls is available, raise error if not."""
    if not HAS_PYGLS:
        raise ImportError(
            "pygls is required for LSP support. "
            "Install with: pip install auto-refactor-ai[lsp]"
        )


class AutoRefactorLanguageServer(LanguageServer):
    """Language server for Auto Refactor AI.

    Provides real-time code analysis with diagnostics and quick fixes.
    """

    def __init__(self):
        check_pygls_available()
        super().__init__(name=SERVER_NAME, version=SERVER_VERSION)
        self.config = load_config(None)
        self._diagnostics_cache: dict = {}

    def get_diagnostics(self, uri: str, content: str) -> List:
        """Analyze content and return LSP diagnostics."""
        # Write content to temp file for analysis
        import os
        import tempfile

        diagnostics = []

        try:
            # Create temp file with content
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(content)
                temp_path = f.name

            # Analyze the file
            issues = analyze_file(
                temp_path,
                max_function_length=self.config.max_function_length,
                max_parameters=self.config.max_parameters,
                max_nesting_depth=self.config.max_nesting_depth,
            )

            # Convert issues to diagnostics
            for issue in issues:
                diagnostic = self._issue_to_diagnostic(issue)
                diagnostics.append(diagnostic)

            # Cache for code actions
            self._diagnostics_cache[uri] = issues

        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception:
                pass

        return diagnostics

    def _issue_to_diagnostic(self, issue: Issue):
        """Convert an Issue to an LSP Diagnostic."""
        # Map severity to LSP severity
        severity_map = {
            Severity.CRITICAL: lsp.DiagnosticSeverity.Error,
            Severity.WARN: lsp.DiagnosticSeverity.Warning,
            Severity.INFO: lsp.DiagnosticSeverity.Information,
        }

        return lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=issue.start_line - 1, character=0),
                end=lsp.Position(line=issue.end_line - 1, character=0),
            ),
            message=issue.message,
            severity=severity_map.get(issue.severity, lsp.DiagnosticSeverity.Information),
            source=SERVER_NAME,
            code=issue.rule_name,
            data={
                "function_name": issue.function_name,
                "rule_name": issue.rule_name,
                "file": issue.file,
            },
        )


# Create server instance
server: Optional[AutoRefactorLanguageServer] = None


def get_server() -> AutoRefactorLanguageServer:
    """Get or create the language server instance."""
    global server
    if server is None:
        check_pygls_available()
        server = AutoRefactorLanguageServer()
        _register_features(server)
    return server


def _register_features(server: AutoRefactorLanguageServer):
    """Register LSP feature handlers."""

    @server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
    def did_open(params: lsp.DidOpenTextDocumentParams):
        """Handle document open - publish diagnostics."""
        doc = params.text_document
        diagnostics = server.get_diagnostics(doc.uri, doc.text)
        server.publish_diagnostics(doc.uri, diagnostics)

    @server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
    def did_save(params: lsp.DidSaveTextDocumentParams):
        """Handle document save - refresh diagnostics."""
        uri = params.text_document.uri
        doc = server.workspace.get_text_document(uri)
        diagnostics = server.get_diagnostics(uri, doc.source)
        server.publish_diagnostics(uri, diagnostics)

    @server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
    def did_change(params: lsp.DidChangeTextDocumentParams):
        """Handle document change - update diagnostics."""
        uri = params.text_document.uri
        doc = server.workspace.get_text_document(uri)
        diagnostics = server.get_diagnostics(uri, doc.source)
        server.publish_diagnostics(uri, diagnostics)

    @server.feature(lsp.TEXT_DOCUMENT_CODE_ACTION)
    def code_action(params: lsp.CodeActionParams) -> List[lsp.CodeAction]:
        """Provide code actions (quick fixes) for diagnostics."""
        uri = params.text_document.uri
        actions = []

        # Get cached issues for this file
        issues = server._diagnostics_cache.get(uri, [])

        for diagnostic in params.context.diagnostics:
            # Find matching issue
            matching_issue = None
            for issue in issues:
                if (
                    issue.start_line - 1 == diagnostic.range.start.line
                    and issue.rule_name == diagnostic.code
                ):
                    matching_issue = issue
                    break

            if matching_issue:
                # Get explanation for the issue
                explanation = get_explanation(matching_issue)

                # Create "Show Explanation" action
                actions.append(
                    lsp.CodeAction(
                        title=f"💡 {explanation.title}",
                        kind=lsp.CodeActionKind.QuickFix,
                        diagnostics=[diagnostic],
                        command=lsp.Command(
                            title="Show Explanation",
                            command="auto-refactor-ai.showExplanation",
                            arguments=[
                                {
                                    "title": explanation.title,
                                    "why": explanation.why_it_matters,
                                    "how": explanation.how_to_fix,
                                }
                            ],
                        ),
                    )
                )

        return actions

    @server.feature(lsp.TEXT_DOCUMENT_HOVER)
    def hover(params: lsp.HoverParams) -> Optional[lsp.Hover]:
        """Provide hover information for issues."""
        uri = params.text_document.uri
        line = params.position.line

        # Find issue at this line
        issues = server._diagnostics_cache.get(uri, [])

        for issue in issues:
            if issue.start_line - 1 <= line <= issue.end_line - 1:
                explanation = get_explanation(issue)

                # Build markdown content
                content = f"## {explanation.title}\n\n"
                content += f"**Why it matters:** {explanation.why_it_matters}\n\n"
                content += "**How to fix:**\n"
                for step in explanation.how_to_fix[:3]:
                    content += f"- {step}\n"

                return lsp.Hover(
                    contents=lsp.MarkupContent(
                        kind=lsp.MarkupKind.Markdown,
                        value=content,
                    )
                )

        return None

    @server.command("auto-refactor-ai.analyze")
    def analyze_command(params):
        """Command to manually trigger analysis."""
        logger.info("Manual analysis triggered")
        # Could trigger full project analysis here
        return {"status": "ok"}


def start_server(transport: str = "stdio", host: str = "127.0.0.1", port: int = 2087):
    """Start the language server.

    Args:
        transport: Communication transport - 'stdio' or 'tcp'
        host: Host for TCP transport
        port: Port for TCP transport
    """
    check_pygls_available()
    srv = get_server()

    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION} ({transport})")

    if transport == "tcp":
        srv.start_tcp(host, port)
    else:
        srv.start_io()


def main():
    """Entry point for running the LSP server standalone."""
    import argparse

    parser = argparse.ArgumentParser(description="Auto Refactor AI Language Server")
    parser.add_argument(
        "--tcp", action="store_true", help="Use TCP transport instead of stdio"
    )
    parser.add_argument("--host", default="127.0.0.1", help="TCP host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=2087, help="TCP port (default: 2087)")

    args = parser.parse_args()

    transport = "tcp" if args.tcp else "stdio"
    start_server(transport=transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
