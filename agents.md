# MMM Team Orchestrator — Agent Guide

## Purpose

This MCP server acts as a **file-based task manager** for multi-agent team orchestration. It is designed to be used by AI coding assistants (e.g. OpenCode, Claude, Copilot) as the coordination backbone between specialized agent teams.

Each team operates independently. The MCP server mediates task assignment, completion, escalation, and commenting — all persisted as JSON files on disk.

---

## Architecture Overview

```
mmm-team-orchestrator/
├── mcp_server.py          # MCP server entry point
├── task_manager.py        # Core task logic (create/complete/comment/escalate)
├── storage.py             # File I/O abstraction
├── models.py              # Task data models (dataclasses)
├── agents.md              # This file — agent instructions
├── requirements.txt       # Python dependencies
├── tasks/                 # Runtime directory (auto-created)
│   ├── <task-id>.json     # One JSON file per task
│   └── index.json         # Global task index
└── logs/
    └── activity.log       # Append-only activity log
```

---

## Teams

Teams are free-form string identifiers. The following are the **recommended defaults**, but any string is valid:

| Team ID         | Responsibility                                      |
|-----------------|-----------------------------------------------------|
| `research`      | Data gathering, web search, analysis                |
| `coding`        | Code generation, refactoring, debugging             |
| `review`        | Code review, QA, test writing                       |
| `devops`        | Deployment, CI/CD, infrastructure                   |
| `orchestrator`  | High-level planning, task decomposition, routing    |

---

## Task Lifecycle

```
  [OPEN] ──► [IN_PROGRESS] ──► [DONE]
                 │
                 └──► [ESCALATED] ──► [IN_PROGRESS] (on new team)
```

1. **OPEN** — Task created, assigned to a team, not yet started
2. **IN_PROGRESS** — Task picked up (optional manual transition)
3. **DONE** — Task completed with an outcome summary
4. **ESCALATED** — Task transferred to another team with a reason comment

---

## MCP Tools Exposed

### `create_task`
Create a new task and assign it to a team.

**Parameters:**
- `title` (string, required) — Short description of the task
- `team` (string, required) — Target team ID
- `description` (string, optional) — Full task details
- `priority` (string, optional) — `low` | `medium` | `high` (default: `medium`)
- `parent_task_id` (string, optional) — Link to a parent task for sub-tasks

**Returns:** Task object with generated `task_id`

---

### `complete_task`
Mark a task as done.

**Parameters:**
- `task_id` (string, required) — ID of the task to complete
- `outcome` (string, required) — Summary of what was accomplished

**Returns:** Updated task object

---

### `comment_and_escalate`
Add a comment to a task and re-assign it to another team.

**Parameters:**
- `task_id` (string, required) — ID of the task
- `comment` (string, required) — Reason for escalation / context note
- `new_team` (string, required) — Team to escalate to

**Returns:** Updated task object

---

### `get_task`
Read the current state of a task.

**Parameters:**
- `task_id` (string, required)

**Returns:** Full task object

---

### `list_tasks`
List tasks, optionally filtered.

**Parameters:**
- `team` (string, optional) — Filter by team
- `status` (string, optional) — Filter by status

**Returns:** Array of task summaries

---

## Task JSON Schema

```json
{
  "task_id": "uuid4",
  "title": "string",
  "description": "string",
  "team": "string",
  "status": "OPEN | IN_PROGRESS | DONE | ESCALATED",
  "priority": "low | medium | high",
  "parent_task_id": "string | null",
  "outcome": "string | null",
  "comments": [
    {
      "timestamp": "ISO8601",
      "author": "string",
      "text": "string",
      "escalated_to": "string | null"
    }
  ],
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the MCP server (stdio mode for OpenCode)
```bash
python mcp_server.py
```

### 3. Register in OpenCode config (`~/.config/opencode/config.json`)
```json
{
  "mcp": {
    "servers": {
      "team-orchestrator": {
        "command": "python",
        "args": ["/path/to/mmm-team-orchestrator/mcp_server.py"],
        "env": {
          "TASKS_DIR": "/path/to/mmm-team-orchestrator/tasks"
        }
      }
    }
  }
}
```

---

## Agent Usage Patterns

### Pattern 1 — Decompose and delegate
The `orchestrator` team creates sub-tasks for other teams:
```
create_task(title="Analyze CSV schema", team="research", parent_task_id="<root-id>")
create_task(title="Generate parser code", team="coding", parent_task_id="<root-id>")
```

### Pattern 2 — Escalate on blocker
A `coding` agent hits a blocker and escalates to `review`:
```
comment_and_escalate(
  task_id="<id>",
  comment="Code written, needs security review before merge",
  new_team="review"
)
```

### Pattern 3 — Complete and report
```
complete_task(task_id="<id>", outcome="Parser implemented, 98% test coverage")
```

---

## Environment Variables

| Variable    | Default              | Description                         |
|-------------|----------------------|-------------------------------------|
| `TASKS_DIR` | `./tasks`            | Directory where task JSON files live |
| `LOGS_DIR`  | `./logs`             | Directory for activity log           |
| `LOG_LEVEL` | `INFO`               | Python logging level                 |
