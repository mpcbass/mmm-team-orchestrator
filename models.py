from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timezone
import uuid


# ---------------------------------------------------------------------------
# Task models
# ---------------------------------------------------------------------------

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
        return cls(
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


# ---------------------------------------------------------------------------
# Chat models
# ---------------------------------------------------------------------------

@dataclass
class ChatMessage:
    timestamp: str
    author_team: str
    text: str

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "author_team": self.author_team,
            "text": self.text,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ChatMessage":
        return cls(
            timestamp=d["timestamp"],
            author_team=d["author_team"],
            text=d["text"],
        )


@dataclass
class Chat:
    title: str
    teams: List[str]
    chat_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: str = "OPEN"
    linked_task_id: Optional[str] = None
    summary: str = ""
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def touch(self):
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "chat_id": self.chat_id,
            "title": self.title,
            "description": self.description,
            "teams": self.teams,
            "status": self.status,
            "linked_task_id": self.linked_task_id,
            "summary": self.summary,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Chat":
        return cls(
            chat_id=d["chat_id"],
            title=d["title"],
            description=d.get("description", ""),
            teams=d.get("teams", []),
            status=d.get("status", "OPEN"),
            linked_task_id=d.get("linked_task_id"),
            summary=d.get("summary", ""),
            messages=[ChatMessage.from_dict(m) for m in d.get("messages", [])],
            created_at=d["created_at"],
            updated_at=d["updated_at"],
        )
