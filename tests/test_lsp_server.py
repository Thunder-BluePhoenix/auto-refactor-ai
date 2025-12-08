"""Tests for the LSP server module (V11)."""


import pytest

from auto_refactor_ai.analyzer import Issue, Severity


class TestLspServerImports:
    """Test LSP server can be imported and handles missing pygls."""

    def test_import_without_pygls(self):
        """Test module handles missing pygls gracefully."""
        # The module should import even without pygls
        from auto_refactor_ai import lsp_server
        assert hasattr(lsp_server, "HAS_PYGLS")

    def test_check_pygls_available(self):
        """Test check function raises when pygls unavailable."""
        from auto_refactor_ai.lsp_server import HAS_PYGLS, check_pygls_available

        if not HAS_PYGLS:
            with pytest.raises(ImportError, match="pygls is required"):
                check_pygls_available()


class TestDiagnosticConversion:
    """Test issue to diagnostic conversion."""

    @pytest.fixture
    def sample_issue(self):
        """Create a sample issue for testing."""
        return Issue(
            severity=Severity.CRITICAL,
            file="test.py",
            function_name="long_function",
            start_line=10,
            end_line=50,
            rule_name="function-too-long",
            message="Function is too long (40 lines)",
            details={"length": 40, "max_length": 30},
        )

    @pytest.mark.skipif(
        not pytest.importorskip("pygls", reason="pygls not installed"),
        reason="pygls not installed"
    )
    def test_issue_to_diagnostic(self, sample_issue):
        """Test converting an Issue to LSP Diagnostic."""
        from auto_refactor_ai.lsp_server import AutoRefactorLanguageServer

        server = AutoRefactorLanguageServer()
        diagnostic = server._issue_to_diagnostic(sample_issue)

        assert diagnostic.message == sample_issue.message
        assert diagnostic.code == sample_issue.rule_name
        assert diagnostic.range.start.line == sample_issue.start_line - 1


class TestServerFeatures:
    """Test LSP server feature handlers."""

    @pytest.mark.skipif(
        not pytest.importorskip("pygls", reason="pygls not installed"),
        reason="pygls not installed"
    )
    def test_server_creation(self):
        """Test server can be created."""
        from auto_refactor_ai.lsp_server import SERVER_NAME, get_server

        server = get_server()
        assert server is not None
        assert server.name == SERVER_NAME

    @pytest.mark.skipif(
        not pytest.importorskip("pygls", reason="pygls not installed"),
        reason="pygls not installed"
    )
    def test_get_diagnostics(self, tmp_path):
        """Test getting diagnostics from file content."""
        from auto_refactor_ai.lsp_server import AutoRefactorLanguageServer

        server = AutoRefactorLanguageServer()

        # Simple code with a long function
        code = '''
def very_long_function():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    line9 = 9
    line10 = 10
    line11 = 11
    line12 = 12
    line13 = 13
    line14 = 14
    line15 = 15
    line16 = 16
    line17 = 17
    line18 = 18
    line19 = 19
    line20 = 20
    line21 = 21
    line22 = 22
    line23 = 23
    line24 = 24
    line25 = 25
    line26 = 26
    line27 = 27
    line28 = 28
    line29 = 29
    line30 = 30
    line31 = 31
    return line31
'''

        diagnostics = server.get_diagnostics("file:///test.py", code)

        # Should find the long function issue
        assert len(diagnostics) >= 1
        assert any("too long" in d.message.lower() or "long" in d.message.lower()
                   for d in diagnostics)


class TestCLIIntegration:
    """Test CLI integration with LSP flags."""

    def test_lsp_flag_exists(self):
        """Test --lsp flag is available."""
        from auto_refactor_ai.cli import create_argument_parser

        parser = create_argument_parser()
        args = parser.parse_args(["--lsp"])

        assert args.lsp is True

    def test_lsp_tcp_flag_exists(self):
        """Test --lsp-tcp flag is available."""
        from auto_refactor_ai.cli import create_argument_parser

        parser = create_argument_parser()
        args = parser.parse_args(["--lsp", "--lsp-tcp"])

        assert args.lsp_tcp is True

    def test_lsp_port_flag_exists(self):
        """Test --lsp-port flag is available."""
        from auto_refactor_ai.cli import create_argument_parser

        parser = create_argument_parser()
        args = parser.parse_args(["--lsp", "--lsp-port", "3000"])

        assert args.lsp_port == 3000


class TestStartServer:
    """Test server startup functions."""

    @pytest.mark.skipif(
        not pytest.importorskip("pygls", reason="pygls not installed"),
        reason="pygls not installed"
    )
    def test_start_server_function_exists(self):
        """Test start_server function exists."""
        from auto_refactor_ai.lsp_server import start_server
        assert callable(start_server)

    @pytest.mark.skipif(
        not pytest.importorskip("pygls", reason="pygls not installed"),
        reason="pygls not installed"
    )
    def test_main_function_exists(self):
        """Test main entry point exists."""
        from auto_refactor_ai.lsp_server import main
        assert callable(main)
