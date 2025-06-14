# SPDX-License-Identifier: AGPL-3.0-only
"""Database connection and ledger storage for FlowZo."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from sqlmodel import Session, SQLModel, create_engine, select

from .models import FlowContext, SessionEvent, SessionRecord


class FlowLedger:
    """FlowZo ledger for storing session data."""
    
    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize ledger with SQLite database."""
        if db_path is None:
            # Default to ~/.flowzo/ledger.db
            flowzo_dir = Path.home() / ".flowzo"
            flowzo_dir.mkdir(exist_ok=True)
            db_path = str(flowzo_dir / "ledger.db")
        
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        
        # Create tables
        SQLModel.metadata.create_all(self.engine)
    
    def create_session_record(
        self,
        session_id: str,
        start_time: datetime,
        duration_seconds: int,
        state: str = "idle",
    ) -> SessionRecord:
        """Create a new session record."""
        record = SessionRecord(
            session_id=session_id,
            start_time=start_time,
            duration_seconds=duration_seconds,
            state=state,
        )
        
        with Session(self.engine) as session:
            session.add(record)
            session.commit()
            session.refresh(record)
        
        return record
    
    def update_session_record(
        self,
        session_id: str,
        end_time: Optional[datetime] = None,
        state: Optional[str] = None,
    ) -> Optional[SessionRecord]:
        """Update an existing session record."""
        with Session(self.engine) as session:
            statement = select(SessionRecord).where(SessionRecord.session_id == session_id)
            record = session.exec(statement).first()
            
            if record:
                if end_time:
                    record.end_time = end_time
                if state:
                    record.state = state
                record.updated_at = datetime.utcnow()
                
                session.add(record)
                session.commit()
                session.refresh(record)
            
            return record
    
    def log_session_event(
        self,
        session_id: str,
        timestamp: float,
        event_type: str,
        state: str,
        data: dict,
    ) -> SessionEvent:
        """Log a session event."""
        event = SessionEvent(
            session_id=session_id,
            timestamp=timestamp,
            event_type=event_type,
            state=state,
            data=json.dumps(data),
        )
        
        with Session(self.engine) as session:
            session.add(event)
            session.commit()
            session.refresh(event)
        
        return event
    
    def log_flow_context(
        self,
        session_id: str,
        context_type: str,
        timestamp: float,
        data: dict,
    ) -> FlowContext:
        """Log flow context data."""
        context = FlowContext(
            session_id=session_id,
            context_type=context_type,
            timestamp=timestamp,
            data=json.dumps(data),
        )
        
        with Session(self.engine) as session:
            session.add(context)
            session.commit()
            session.refresh(context)
        
        return context
    
    def get_session_events(self, session_id: str) -> List[SessionEvent]:
        """Get all events for a session."""
        with Session(self.engine) as session:
            statement = select(SessionEvent).where(SessionEvent.session_id == session_id)
            return list(session.exec(statement).all())
    
    def get_recent_sessions(self, limit: int = 10) -> List[SessionRecord]:
        """Get recent session records."""
        with Session(self.engine) as session:
            statement = (
                select(SessionRecord)
                .order_by(SessionRecord.created_at.desc())
                .limit(limit)
            )
            return list(session.exec(statement).all())
    
    def get_session_record(self, session_id: str) -> Optional[SessionRecord]:
        """Get a specific session record."""
        with Session(self.engine) as session:
            statement = select(SessionRecord).where(SessionRecord.session_id == session_id)
            return session.exec(statement).first() 