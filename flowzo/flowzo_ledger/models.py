# SPDX-License-Identifier: AGPL-3.0-only
"""SQLModel models for FlowZo ledger storage."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SessionRecord(SQLModel, table=True):
    """Session record in the ledger."""
    
    __tablename__ = "sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, unique=True)
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: int
    state: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SessionEvent(SQLModel, table=True):
    """Individual session event in the ledger."""
    
    __tablename__ = "session_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    timestamp: float
    event_type: str
    state: str
    data: str  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FlowContext(SQLModel, table=True):
    """Flow context for session replay."""
    
    __tablename__ = "flow_contexts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    context_type: str  # "keystroke", "ide_state", "window_focus", etc.
    timestamp: float
    data: str  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow) 