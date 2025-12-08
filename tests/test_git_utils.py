"""Tests for git_utils module (V9)."""

import os
import pytest
from unittest.mock import patch, MagicMock
from auto_refactor_ai.git_utils import is_git_repo, get_changed_files


class TestGitUtils:

    @patch("subprocess.run")
    def test_is_git_repo_true(self, mock_run):
        """Test is_git_repo when true."""
        mock_run.return_value.returncode = 0
        assert is_git_repo(".") is True

    @patch("subprocess.run")
    def test_is_git_repo_false(self, mock_run):
        """Test is_git_repo when false."""
        mock_run.return_value.returncode = 128
        assert is_git_repo(".") is False

    @patch("subprocess.run")
    def test_is_git_repo_exception(self, mock_run):
        """Test is_git_repo handles exception."""
        mock_run.side_effect = FileNotFoundError
        assert is_git_repo(".") is False

    @patch("auto_refactor_ai.git_utils.is_git_repo")
    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_get_changed_files_modified(self, mock_exists, mock_run, mock_is_git):
        """Test getting modified files."""
        mock_is_git.return_value = True
        mock_exists.return_value = True

        # Mock git diff output
        mock_diff = MagicMock()
        mock_diff.stdout = "file1.py\nfile2.py\n"

        # Mock git rev-parse output
        mock_root = MagicMock()
        mock_root.stdout = "/repo/root\n"

        mock_run.side_effect = [mock_diff, mock_root]

        files = get_changed_files(".")

        assert len(files) == 2
        # Paths will be constructed with os.path.join, so check endings
        assert any(f.endswith("file1.py") for f in files)
        assert any(f.endswith("file2.py") for f in files)

    @patch("auto_refactor_ai.git_utils.is_git_repo")
    @patch("subprocess.run")
    def test_get_changed_files_staged(self, mock_run, mock_is_git):
        """Test getting staged files passes correct flag."""
        mock_is_git.return_value = True

        mock_diff = MagicMock()
        mock_diff.stdout = ""
        mock_root = MagicMock()
        mock_root.stdout = "/root"

        mock_run.side_effect = [mock_diff, mock_root]

        get_changed_files(".", staged=True)

        # Verify git diff called with --cached
        cmd = mock_run.call_args_list[0][0][0]
        assert "--cached" in cmd

    @patch("auto_refactor_ai.git_utils.is_git_repo")
    def test_get_changed_files_not_repo(self, mock_is_git):
        """Test returns empty if not a repo."""
        mock_is_git.return_value = False
        assert get_changed_files(".") == []
