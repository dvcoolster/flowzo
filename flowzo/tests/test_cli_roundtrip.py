# SPDX-License-Identifier: AGPL-3.0-only
"""Test CLI roundtrip functionality."""

import subprocess
import sys
from pathlib import Path


def test_cli_start_exits_zero() -> None:
    """Test that 'flowzo start' exits with code 0."""
    # Run the CLI command
    result = subprocess.run(
        [sys.executable, "-m", "flowzo_cli.main", "start", "--duration", "1"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    # Assert exit code is 0
    assert result.returncode == 0
    
    # Assert expected output patterns
    assert "Entering flow..." in result.stdout
    assert "Session complete!" in result.stdout


def test_cli_next_exits_zero() -> None:
    """Test that 'flowzo next' exits with code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "flowzo_cli.main", "next"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
        timeout=5,
    )
    
    assert result.returncode == 0
    assert "Integration not yet implemented" in result.stdout 