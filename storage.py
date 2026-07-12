import json
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict
from models import Task

logger = logging.getLogger(__name__)

TASKS_DIR = Path(os.environ.get("TASKS_DIR", "./tasks"))
LOGS_DIR = Path(os.environ.get("LOGS_DIR", "./logs"))
INDEX_FILE = TASKS_DIR / "index.json"
LOG_FILE = LOGS_DIR / "activity.log"


def _ensure_dirs():
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _task_path(task_id: str) -> Path:
    return TASKS_DIR / f"{task_id}.json"


def load_index() -> Dict[str, dict]:
    _ensure_dirs()
    if not INDEX_FILE.exists():
        return {}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_index(index: Dict[str, dict]):
    _ensure_dirs()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
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


def _append_log(message: str):
    _ensure_dirs()
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")
