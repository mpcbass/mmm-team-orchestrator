# MMM Team Orchestrator

A minimal **MCP (Model Context Protocol) server** that acts as a file-based task manager for multi-agent team orchestration.

Designed for use with **OpenCode**, Claude, or any MCP-compatible AI assistant.

## Quick Start

```cmd
# Python 3.9+ required, no extra dependencies
python mcp_server.py
```

## Register with OpenCode on Windows

OpenCode legge la config da:
```
C:\Users\<you>\.config\opencode\opencode.jsonc
```

Schema richiesto da OpenCode: `command` è un **array** (non stringa), e `enabled` è **obbligatorio**.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "team-orchestrator": {
      "enabled": true,
      "command": [
        "cmd",
        "/c",
        "D:\\projects\\opencode\\mmm-team-orchestrator\\mcp_server.cmd"
      ],
      "env": {
        "TASKS_DIR": "D:\\projects\\opencode\\mmm-team-orchestrator\\tasks"
      }
    }
  }
}
```

> **Note**: `command` is an array where first element is the executable and the rest are arguments.  
> Use double backslash `\\` in JSON paths on Windows.

## Test manuale da PowerShell

```powershell
cd D:\projects\opencode\mmm-team-orchestrator
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python mcp_server.py
```

Risposta attesa: `{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05", ...}}`

Poi in OpenCode digita `/mcp` per verificare che il server sia connesso.

## Tools

| Tool | Description |
|------|-------------|
| `create_task` | Create a task assigned to a team |
| `complete_task` | Mark task as DONE with outcome |
| `comment_and_escalate` | Add comment and re-assign to another team |
| `get_task` | Fetch full task details |
| `list_tasks` | List all tasks with optional filters |

See [agents.md](./agents.md) for full documentation.
