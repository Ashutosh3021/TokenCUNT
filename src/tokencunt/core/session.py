"""Session tracking module with persistence."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from pathlib import Path
import json


class TokenUsage(BaseModel):
    """Token usage with input/output tracking."""
    input_tokens: int = 0
    output_tokens: int = 0
    
    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens
    
    def add(self, other: "TokenUsage"):
        """Add another TokenUsage to this one."""
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens


class RequestRecord(BaseModel):
    """Record of a single API request."""
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    estimated_tokens: Optional[int] = None
    prompt: str
    response: Optional[str] = None


class Session(BaseModel):
    """Session tracking all operations."""
    session_id: str
    created_at: datetime
    updated_at: datetime
    requests: List[RequestRecord] = []
    total_usage: TokenUsage = TokenUsage()
    
    @property
    def request_count(self) -> int:
        return len(self.requests)
    
    def add_request(self, record: RequestRecord):
        """Add a request record to the session."""
        self.requests.append(record)
        self.total_usage.add(TokenUsage(
            input_tokens=record.input_tokens,
            output_tokens=record.output_tokens
        ))
        self.updated_at = datetime.now()


class SessionManager:
    """Manages session persistence in JSON files."""
    
    def __init__(self, session_dir: Path = None):
        """
        Initialize session manager.
        
        Args:
            session_dir: Directory to store session files
        """
        if session_dir is None:
            session_dir = Path.home() / ".tokencunt" / "sessions"
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def save_session(self, session: Session):
        """Save session to JSON file."""
        filepath = self.session_dir / f"{session.session_id}.json"
        with open(filepath, "w") as f:
            json.dump(session.model_dump(mode="json"), f, indent=2, default=str)
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load session from JSON file."""
        filepath = self.session_dir / f"{session_id}.json"
        if not filepath.exists():
            return None
        with open(filepath, "r") as f:
            data = json.load(f)
        return Session(**data)
    
    def create_session(self) -> Session:
        """Create a new session."""
        session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        session = Session(
            session_id=session_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.save_session(session)
        return session
    
    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        return [f.stem for f in self.session_dir.glob("*.json")]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        filepath = self.session_dir / f"{session_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
