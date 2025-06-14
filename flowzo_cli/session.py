# SPDX-License-Identifier: AGPL-3.0-only
"""FlowZo Session Engine - Finite State Machine for focus sessions."""

import asyncio
import json
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class SessionState(str, Enum):
    """Session states in the FSM."""
    IDLE = "idle"
    PRIMING = "priming"
    ACTIVE = "active"
    COOLDOWN = "cooldown"


class SessionEvent(BaseModel):
    """Session event for JSON output."""
    timestamp: float
    session_id: str
    state: SessionState
    event_type: str
    data: Dict[str, Any]


class SessionEngine:
    """Finite State Machine for managing focus sessions."""
    
    def __init__(self, session_id: Optional[str] = None, ledger=None) -> None:
        """Initialize session engine."""
        self.session_id = session_id or f"session_{int(time.time())}"
        self.state = SessionState.IDLE
        self.start_time: Optional[float] = None
        self.duration: int = 0
        self.events: list[SessionEvent] = []
        self.ledger = ledger  # Optional FlowLedger instance
    
    def _emit_event(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> SessionEvent:
        """Emit a session event."""
        event = SessionEvent(
            timestamp=time.time(),
            session_id=self.session_id,
            state=self.state,
            event_type=event_type,
            data=data or {},
        )
        self.events.append(event)
        
        # Log to ledger if available
        if self.ledger:
            self.ledger.log_session_event(
                session_id=self.session_id,
                timestamp=event.timestamp,
                event_type=event_type,
                state=self.state,
                data=data or {},
            )
        
        return event
    
    def transition_to(self, new_state: SessionState) -> SessionEvent:
        """Transition to a new state."""
        old_state = self.state
        self.state = new_state
        return self._emit_event(
            "state_transition",
            {"from_state": old_state, "to_state": new_state},
        )
    
    async def start_session(self, duration: int, priming_duration: int = 5) -> None:
        """Start a complete focus session."""
        if self.state != SessionState.IDLE:
            raise ValueError(f"Cannot start session from state {self.state}")
        
        self.duration = duration
        self.start_time = time.time()
        
        # Create session record in ledger
        if self.ledger:
            self.ledger.create_session_record(
                session_id=self.session_id,
                start_time=datetime.fromtimestamp(self.start_time),
                duration_seconds=duration,
                state="priming",
            )
        
        # Priming phase
        self.transition_to(SessionState.PRIMING)
        self._emit_event("session_started", {"duration": duration, "priming_duration": priming_duration})
        
        await asyncio.sleep(priming_duration)
        
        # Active phase
        self.transition_to(SessionState.ACTIVE)
        self._emit_event("focus_phase_started", {"remaining_seconds": duration})
        
        await asyncio.sleep(duration)
        
        # Cooldown phase
        self.transition_to(SessionState.COOLDOWN)
        self._emit_event("cooldown_started", {"cooldown_duration": 3})
        
        await asyncio.sleep(3)
        
        # Back to idle
        self.transition_to(SessionState.IDLE)
        self._emit_event("session_completed", {"total_duration": time.time() - self.start_time})
        
        # Update session record in ledger
        if self.ledger:
            self.ledger.update_session_record(
                session_id=self.session_id,
                end_time=datetime.fromtimestamp(time.time()),
                state="completed",
            )
    
    def abort_session(self) -> SessionEvent:
        """Abort the current session."""
        if self.state == SessionState.IDLE:
            raise ValueError("No active session to abort")
        
        event = self._emit_event("session_aborted", {"aborted_from_state": self.state})
        self.state = SessionState.IDLE
        return event
    
    def get_status(self) -> Dict[str, Any]:
        """Get current session status."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        remaining = max(0, self.duration - elapsed) if self.duration else 0
        
        return {
            "session_id": self.session_id,
            "state": self.state,
            "elapsed_seconds": elapsed,
            "remaining_seconds": remaining,
            "total_duration": self.duration,
        }
    
    def export_events_json(self) -> str:
        """Export all events as JSON."""
        return json.dumps([event.model_dump() for event in self.events], indent=2) 