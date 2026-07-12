import logging
from typing import Optional
from models import Task, Comment
from storage import save_task, load_task, list_tasks as storage_list
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"OPEN", "IN_PROGRESS", "DONE", "ESCALATED"}


def create_task(
    title: str,
    team: str,
    description: str = "",
    priority: str = "medium",
    parent_task_id: Optional[str] = None,
) -> dict:
    if not title.strip():
        raise ValueError("title cannot be empty")
    if not team.strip():
        raise ValueError("team cannot be empty")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"priority must be one of {VALID_PRIORITIES}")
    task = Task(
        title=title.strip(),
        team=team.strip(),
        description=description,
        priority=priority,
        parent_task_id=parent_task_id,
    )
    save_task(task)
    logger.info("Created task %s for team %s", task.task_id, task.team)
    return task.to_dict()


def complete_task(task_id: str, outcome: str) -> dict:
    if not outcome.strip():
        raise ValueError("outcome cannot be empty")
    task = load_task(task_id)
    if task is None:
        raise KeyError(f"Task {task_id} not found")
    if task.status == "DONE":
        raise ValueError(f"Task {task_id} is already DONE")
    task.status = "DONE"
    task.outcome = outcome.strip()
    task.touch()
    save_task(task)
    logger.info("Completed task %s", task_id)
    return task.to_dict()


def comment_and_escalate(task_id: str, comment: str, new_team: str) -> dict:
    if not comment.strip():
        raise ValueError("comment cannot be empty")
    if not new_team.strip():
        raise ValueError("new_team cannot be empty")
    task = load_task(task_id)
    if task is None:
        raise KeyError(f"Task {task_id} not found")
    if task.status == "DONE":
        raise ValueError(f"Cannot escalate a DONE task")
    old_team = task.team
    c = Comment(
        timestamp=datetime.now(timezone.utc).isoformat(),
        author=old_team,
        text=comment.strip(),
        escalated_to=new_team.strip(),
    )
    task.comments.append(c)
    task.team = new_team.strip()
    task.status = "ESCALATED"
    task.touch()
    save_task(task)
    logger.info("Escalated task %s from %s to %s", task_id, old_team, new_team)
    return task.to_dict()


def get_task(task_id: str) -> dict:
    task = load_task(task_id)
    if task is None:
        raise KeyError(f"Task {task_id} not found")
    return task.to_dict()


def list_tasks(team: Optional[str] = None, status: Optional[str] = None) -> list:
    return storage_list(team=team, status=status)
