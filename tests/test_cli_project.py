import tempfile
from pathlib import Path
from unittest.mock import patch


class TestProjectCLI:

    def test_main_with_project_flag(self, capsys):
        """Test main entry point with --project flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy file
            Path(temp_dir, "test.py").write_text("def foo(): pass")

            with patch("sys.argv", ["auto-refactor-ai", temp_dir, "--project"]):
                from auto_refactor_ai.cli import main

                try:
                    main()
                except SystemExit:
                    pass

            captured = capsys.readouterr()
            assert "PROJECT-LEVEL ANALYSIS" in captured.out
            assert "Files Analyzed" in captured.out

    def test_main_with_find_duplicates_flag(self, capsys):
        """Test main entry point with --find-duplicates flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy file
            Path(temp_dir, "test.py").write_text("def foo(): pass")

            with patch("sys.argv", ["auto-refactor-ai", temp_dir, "--find-duplicates"]):
                from auto_refactor_ai.cli import main

                try:
                    main()
                except SystemExit:
                    pass

            captured = capsys.readouterr()
            assert "PROJECT-LEVEL ANALYSIS" in captured.out
