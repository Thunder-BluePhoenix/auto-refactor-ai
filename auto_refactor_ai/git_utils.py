"""Git integration utilities (V9)."""

import os
import subprocess
from pathlib import Path
from typing import List


def is_git_repo(path: str) -> bool:
    """Check if the given path is part of a git repository.

    Args:
        path: Path to check

    Returns:
        True if inside a git repo, False otherwise
    """
    try:
        # Check if git is installed and path is in a repo
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def get_changed_files(path: str, staged: bool = False) -> List[str]:
    """Get list of changed Python files.

    Args:
        path: Root path to check from
        staged: If True, check staged files. If False, check working tree.

    Returns:
        List of absolute paths to changed Python files
    """
    if not is_git_repo(path):
        return []

    cmd = ["git", "diff", "--name-only"]
    if staged:
        cmd.append("--cached")

    # Filter for .py files
    cmd.append("--")
    cmd.append("*.py")

    try:
        result = subprocess.run(
            cmd, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )

        # Parse output relative paths and convert to absolute
        files = []
        root_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        git_root = root_result.stdout.strip()

        for relative_path in result.stdout.splitlines():
            if relative_path.strip():
                full_path = os.path.join(git_root, relative_path)
                # Only include existing files (files might be deleted)
                if os.path.exists(full_path):
                    files.append(full_path)

        return files

    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
