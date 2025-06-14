# SPDX-License-Identifier: AGPL-3.0-only
"""Integration tests for desktop overlay functionality."""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

from flowzo_cli.session import SessionEngine


@pytest.mark.asyncio
async def test_session_engine_json_output():
    """Test that SessionEngine produces JSON output compatible with desktop overlay."""
    engine = SessionEngine("desktop_test")
    
    # Run a very short session
    await engine.start_session(duration=1, priming_duration=0.1)
    
    # Export events as JSON
    json_output = engine.export_events_json()
    events = json.loads(json_output)
    
    # Verify JSON structure matches desktop expectations
    assert len(events) > 0
    
    for event in events:
        assert "timestamp" in event
        assert "session_id" in event
        assert "state" in event
        assert "event_type" in event
        assert "data" in event
        
        # Verify session_id matches
        assert event["session_id"] == "desktop_test"
        
        # Verify state is valid
        assert event["state"] in ["idle", "priming", "active", "cooldown"]


def test_session_state_format():
    """Test that session state format matches Tauri IPC expectations."""
    engine = SessionEngine("format_test")
    
    # Get status in expected format
    status = engine.get_status()
    
    # Verify all required fields are present
    required_fields = [
        "session_id",
        "state", 
        "elapsed_seconds",
        "remaining_seconds",
        "total_duration"
    ]
    
    for field in required_fields:
        assert field in status
    
    # Verify types
    assert isinstance(status["session_id"], str)
    assert isinstance(status["state"], str)
    assert isinstance(status["elapsed_seconds"], (int, float))
    assert isinstance(status["remaining_seconds"], (int, float))
    assert isinstance(status["total_duration"], int)


@pytest.mark.skipif(
    not Path("flowzo_desktop/Cargo.toml").exists(),
    reason="Desktop overlay not available"
)
def test_tauri_config_valid():
    """Test that Tauri configuration is valid."""
    config_path = Path("flowzo_desktop/tauri.conf.json")
    assert config_path.exists(), "Tauri config file should exist"
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Verify essential configuration
    assert config["tauri"]["bundle"]["identifier"] == "com.flowzo.desktop"
    assert config["package"]["productName"] == "FlowZo"
    
    # Verify window configuration for overlay
    windows = config["tauri"]["windows"]
    assert len(windows) == 1
    
    window = windows[0]
    assert window["decorations"] is False
    assert window["alwaysOnTop"] is True
    assert window["transparent"] is True
    assert window["width"] == 320
    assert window["height"] == 320


@pytest.mark.skipif(
    not Path("flowzo_desktop/package.json").exists(),
    reason="Desktop frontend not available"
)
def test_frontend_dependencies():
    """Test that frontend dependencies are properly configured."""
    package_path = Path("flowzo_desktop/package.json")
    assert package_path.exists(), "Package.json should exist"
    
    with open(package_path) as f:
        package = json.load(f)
    
    # Verify essential dependencies
    assert "@tauri-apps/api" in package["dependencies"]
    assert "@sveltejs/kit" in package["devDependencies"]
    assert "svelte" in package["devDependencies"]
    
    # Verify scripts
    scripts = package["scripts"]
    assert "dev" in scripts
    assert "build" in scripts
    assert "tauri" in scripts


def test_rust_workspace_config():
    """Test that Rust workspace is properly configured."""
    cargo_path = Path("Cargo.toml")
    assert cargo_path.exists(), "Workspace Cargo.toml should exist"
    
    with open(cargo_path) as f:
        content = f.read()
    
    # Verify workspace configuration
    assert "[workspace]" in content
    assert "flowzo_desktop" in content
    assert "resolver = \"2\"" in content 