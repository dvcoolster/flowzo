# SPDX-License-Identifier: AGPL-3.0-only
"""Integration tests for FlowZo ledger storage."""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from flowzo_cli.session import SessionEngine
from flowzo_ledger.database import FlowLedger


@pytest.fixture
def temp_ledger():
    """Create a temporary ledger for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        ledger = FlowLedger(tmp.name)
        yield ledger
        # Cleanup
        Path(tmp.name).unlink(missing_ok=True)


def test_ledger_session_record_creation(temp_ledger):
    """Test creating and retrieving session records."""
    session_id = "test_session_123"
    start_time = datetime.utcnow()
    
    # Create session record
    record = temp_ledger.create_session_record(
        session_id=session_id,
        start_time=start_time,
        duration_seconds=1500,
        state="active",
    )
    
    assert record.session_id == session_id
    assert record.start_time == start_time
    assert record.duration_seconds == 1500
    assert record.state == "active"
    
    # Retrieve session record
    retrieved = temp_ledger.get_session_record(session_id)
    assert retrieved is not None
    assert retrieved.session_id == session_id


def test_ledger_session_events(temp_ledger):
    """Test logging and retrieving session events."""
    session_id = "test_events_session"
    
    # Log some events
    event1 = temp_ledger.log_session_event(
        session_id=session_id,
        timestamp=1234567890.0,
        event_type="session_started",
        state="priming",
        data={"duration": 1500},
    )
    
    event2 = temp_ledger.log_session_event(
        session_id=session_id,
        timestamp=1234567895.0,
        event_type="state_transition",
        state="active",
        data={"from_state": "priming", "to_state": "active"},
    )
    
    # Retrieve events
    events = temp_ledger.get_session_events(session_id)
    assert len(events) == 2
    assert events[0].event_type == "session_started"
    assert events[1].event_type == "state_transition"


def test_ledger_flow_context(temp_ledger):
    """Test logging flow context data."""
    session_id = "test_context_session"
    
    # Log flow context
    context = temp_ledger.log_flow_context(
        session_id=session_id,
        context_type="keystroke",
        timestamp=1234567890.0,
        data={"key": "ctrl+s", "file": "main.py"},
    )
    
    assert context.session_id == session_id
    assert context.context_type == "keystroke"
    assert '"key": "ctrl+s"' in context.data


@pytest.mark.asyncio
async def test_session_engine_with_ledger(temp_ledger):
    """Test SessionEngine integration with ledger."""
    engine = SessionEngine("integration_test", ledger=temp_ledger)
    
    # Run a short session
    await engine.start_session(duration=1, priming_duration=0.1)
    
    # Check session record was created
    record = temp_ledger.get_session_record("integration_test")
    assert record is not None
    assert record.session_id == "integration_test"
    assert record.state == "completed"
    assert record.end_time is not None
    
    # Check events were logged
    events = temp_ledger.get_session_events("integration_test")
    assert len(events) >= 4  # session_started, transitions, session_completed
    
    event_types = [event.event_type for event in events]
    assert "session_started" in event_types
    assert "session_completed" in event_types


def test_ledger_recent_sessions(temp_ledger):
    """Test retrieving recent sessions."""
    # Create multiple session records
    for i in range(5):
        temp_ledger.create_session_record(
            session_id=f"session_{i}",
            start_time=datetime.utcnow(),
            duration_seconds=1500,
        )
    
    # Get recent sessions
    recent = temp_ledger.get_recent_sessions(limit=3)
    assert len(recent) == 3
    
    # Should be ordered by created_at desc
    assert recent[0].session_id == "session_4"
    assert recent[1].session_id == "session_3"
    assert recent[2].session_id == "session_2" 