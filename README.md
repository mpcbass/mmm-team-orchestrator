# MMM Team Orchestrator

A minimal **MCP (Model Context Protocol) server** that acts as a file-based task manager for multi-agent team orchestration.

Designed for use with **OpenCode**, Claude, or any MCP-compatible AI assistant.

## Quick Start

```bash
# Python 3.9+ required, no extra dependencies
python mcp_server.py
```

## Register with OpenCode

Add to `~/.config/opencode/config.json`:

```json
{
  "mcp": {
    "servers": {
      "team-orchestrator": {
        "command": "python",
        "args": ["/absolute/path/to/mmm-team-orchestrator/mcp_server.py"],
        "env": {
          "TASKS_DIR": "/absolute/path/to/mmm-team-orchestrator/tasks"
        }
      }
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `create_task` | Create a task assigned to a team |
| `complete_task` | Mark task as DONE with outcome |
| `comment_and_escalate` | Add comment and re-assign to another team |
| `get_task` | Fetch full task details |
| `list_tasks` | List all tasks with optional filters |

See [agents.md](./agents.md) for full documentation.
