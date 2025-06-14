# SPDX-License-Identifier: AGPL-3.0-only
"""Test SessionEngine FSM functionality."""

import asyncio
import json
import pytest

from flowzo_cli.session import SessionEngine, SessionState


@pytest.mark.asyncio
async def test_session_engine_full_cycle() -> None:
    """Test complete session cycle: idle → priming → active → cooldown → idle."""
    engine = SessionEngine("test_session")
    
    # Initial state
    assert engine.state == SessionState.IDLE
    assert len(engine.events) == 0
    
    # Run a short session
    await engine.start_session(duration=1, priming_duration=0.1)
    
    # Final state
    assert engine.state == SessionState.IDLE
    
    # Check events were emitted
    assert len(engine.events) >= 6  # state transitions + session events
    
    # Verify state transitions occurred
    event_types = [event.event_type for event in engine.events]
    assert "session_started" in event_types
    assert "focus_phase_started" in event_types
    assert "cooldown_started" in event_types
    assert "session_completed" in event_types


def test_session_engine_abort() -> None:
    """Test session abort functionality."""
    engine = SessionEngine()
    
    # Transition to active state manually
    engine.transition_to(SessionState.ACTIVE)
    assert engine.state == SessionState.ACTIVE
    
    # Abort session
    abort_event = engine.abort_session()
    assert engine.state == SessionState.IDLE
    assert abort_event.event_type == "session_aborted"
    assert abort_event.data["aborted_from_state"] == SessionState.ACTIVE


def test_session_engine_status() -> None:
    """Test session status reporting."""
    engine = SessionEngine("status_test")
    
    status = engine.get_status()
    assert status["session_id"] == "status_test"
    assert status["state"] == SessionState.IDLE
    assert status["elapsed_seconds"] == 0
    assert status["remaining_seconds"] == 0


def test_session_engine_json_export() -> None:
    """Test JSON export of session events."""
    engine = SessionEngine()
    
    # Generate some events
    engine.transition_to(SessionState.PRIMING)
    engine.transition_to(SessionState.ACTIVE)
    engine.transition_to(SessionState.IDLE)
    
    # Export as JSON
    json_output = engine.export_events_json()
    events = json.loads(json_output)
    
    assert len(events) == 3
    assert all("timestamp" in event for event in events)
    assert all("session_id" in event for event in events)
    assert events[0]["event_type"] == "state_transition"


def test_session_engine_invalid_start() -> None:
    """Test that starting session from non-idle state raises error."""
    engine = SessionEngine()
    engine.state = SessionState.ACTIVE
    
    with pytest.raises(ValueError, match="Cannot start session from state"):
        asyncio.run(engine.start_session(5))


def test_session_engine_invalid_abort() -> None:
    """Test that aborting from idle state raises error."""
    engine = SessionEngine()
    
    with pytest.raises(ValueError, match="No active session to abort"):
        engine.abort_session() 