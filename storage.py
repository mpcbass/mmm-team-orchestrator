import json
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict
from models import Task, Chat

logger = logging.getLogger(__name__)

_BASE = Path(__file__).resolve().parent


def _tasks_dir() -> Path:
    v = os.environ.get("TASKS_DIR", "").strip()
    return Path(v) if v else _BASE / "tasks"


def _chats_dir() -> Path:
    v = os.environ.get("CHATS_DIR", "").strip()
    return Path(v) if v else _BASE / "chats"


def _logs_dir() -> Path:
    v = os.environ.get("LOGS_DIR", "").strip()
    return Path(v) if v else _BASE / "logs"


def _index_file() -> Path:
    return _tasks_dir() / "index.json"


def _chats_index_file() -> Path:
    return _chats_dir() / "index.json"


def _log_file() -> Path:
    return _logs_dir() / "activity.log"


def _ensure_dirs():
    _tasks_dir().mkdir(parents=True, exist_ok=True)
    _chats_dir().mkdir(parents=True, exist_ok=True)
    _logs_dir().mkdir(parents=True, exist_ok=True)


def _task_path(task_id: str) -> Path:
    return _tasks_dir() / f"{task_id}.json"


def _chat_path(chat_id: str) -> Path:
    return _chats_dir() / f"{chat_id}.json"


# ---------------------------------------------------------------------------
# Task I/O
# ---------------------------------------------------------------------------

def load_index() -> Dict[str, dict]:
    _ensure_dirs()
    idx = _index_file()
    if not idx.exists():
        return {}
    with open(idx, "r", encoding="utf-8") as f:
        return json.load(f)


def save_index(index: Dict[str, dict]):
    _ensure_dirs()
    with open(_index_file(), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)


def save_task(task: Task):
    _ensure_dirs()
    with open(_task_path(task.task_id), "w", encoding="utf-8") as f:
        json.dump(task.to_dict(), f, indent=2)
    index = load_index()
    index[task.task_id] = {
        "task_id": task.task_id,
        "title": task.title,
        "team": task.team,
        "status": task.status,
        "priority": task.priority,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
    save_index(index)
    _append_log(f"SAVE task={task.task_id} status={task.status} team={task.team}")


def load_task(task_id: str) -> Optional[Task]:
    path = _task_path(task_id)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Task.from_dict(data)


def list_tasks(team: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
    index = load_index()
    results = list(index.values())
    if team:
        results = [t for t in results if t["team"] == team]
    if status:
        results = [t for t in results if t["status"] == status]
    return results


# ---------------------------------------------------------------------------
# Chat I/O
# ---------------------------------------------------------------------------

def load_chats_index() -> Dict[str, dict]:
    _ensure_dirs()
    idx = _chats_index_file()
    if not idx.exists():
        return {}
    with open(idx, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chats_index(index: Dict[str, dict]):
    _ensure_dirs()
    with open(_chats_index_file(), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)


def save_chat(chat: Chat):
    _ensure_dirs()
    with open(_chat_path(chat.chat_id), "w", encoding="utf-8") as f:
        json.dump(chat.to_dict(), f, indent=2)
    index = load_chats_index()
    index[chat.chat_id] = {
        "chat_id": chat.chat_id,
        "title": chat.title,
        "teams": chat.teams,
        "status": chat.status,
        "linked_task_id": chat.linked_task_id,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
    }
    save_chats_index(index)
    _append_log(f"SAVE chat={chat.chat_id} status={chat.status} teams={chat.teams}")


def load_chat(chat_id: str) -> Optional[Chat]:
    path = _chat_path(chat_id)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Chat.from_dict(data)


def list_chats(team: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
    index = load_chats_index()
    results = list(index.values())
    if team:
        results = [r for r in results if team in r.get("teams", [])]
    if status:
        results = [r for r in results if r["status"] == status]
    return results


# ---------------------------------------------------------------------------
# Log
# ---------------------------------------------------------------------------

def _append_log(message: str):
    _ensure_dirs()
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat()
    with open(_log_file(), "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")
