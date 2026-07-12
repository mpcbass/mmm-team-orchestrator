from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timezone
import uuid


@dataclass
class Comment:
    timestamp: str
    author: str
    text: str
    escalated_to: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "author": self.author,
            "text": self.text,
            "escalated_to": self.escalated_to,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Comment":
        return cls(
            timestamp=d["timestamp"],
            author=d["author"],
            text=d["text"],
            escalated_to=d.get("escalated_to"),
        )


@dataclass
class Task:
    title: str
    team: str
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: str = "OPEN"
    priority: str = "medium"
    parent_task_id: Optional[str] = None
    outcome: Optional[str] = None
    comments: List[Comment] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def touch(self):
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "team": self.team,
            "status": self.status,
            "priority": self.priority,
            "parent_task_id": self.parent_task_id,
            "outcome": self.outcome,
            "comments": [c.to_dict() for c in self.comments],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        t = cls(
            task_id=d["task_id"],
            title=d["title"],
            description=d.get("description", ""),
            team=d["team"],
            status=d.get("status", "OPEN"),
            priority=d.get("priority", "medium"),
            parent_task_id=d.get("parent_task_id"),
            outcome=d.get("outcome"),
            comments=[Comment.from_dict(c) for c in d.get("comments", [])],
            created_at=d["created_at"],
            updated_at=d["updated_at"],
        )
        return t
