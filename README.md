# MMM Team Orchestrator

A minimal **MCP (Model Context Protocol) server** that acts as a file-based task manager for multi-agent team orchestration.

Designed for use with **OpenCode**, Claude, or any MCP-compatible AI assistant.

## Quick Start

```cmd
# Python 3.9+ required, no extra dependencies
python mcp_server.py
```

## Register with OpenCode on Windows

OpenCode su Windows legge la config da `%APPDATA%\opencode\config.json`  
(es. `C:\Users\MatTeo\AppData\Roaming\opencode\config.json`)

**Usa `mcp_server.cmd` come comando** — questo risolve sia il problema del `cwd` che quello di `python` non trovato:

```json
{
  "mcp": {
    "servers": {
      "team-orchestrator": {
        "command": "C:\\Users\\MatTeo\\mmm-team-orchestrator\\mcp_server.cmd",
        "args": [],
        "env": {
          "TASKS_DIR": "C:\\Users\\MatTeo\\mmm-team-orchestrator\\tasks"
        }
      }
    }
  }
}
```

> **Nota**: usa sempre doppio backslash `\\` nei path JSON su Windows.

## Alternativa: usare Python direttamente con cwd

```json
{
  "mcp": {
    "servers": {
      "team-orchestrator": {
        "command": "python",
        "args": ["mcp_server.py"],
        "cwd": "C:\\Users\\MatTeo\\mmm-team-orchestrator",
        "env": {
          "TASKS_DIR": "C:\\Users\\MatTeo\\mmm-team-orchestrator\\tasks"
        }
      }
    }
  }
}
```

## Test manuale (verifica che funzioni prima di aprire OpenCode)

```cmd
cd C:\Users\MatTeo\mmm-team-orchestrator
echo {"jsonrpc":"2.0","id":1,"method":"initialize","params":{}} | python mcp_server.py
```

Dovresti vedere una risposta JSON con `protocolVersion: "2024-11-05"`.

## Tools

| Tool | Description |
|------|-------------|
| `create_task` | Create a task assigned to a team |
| `complete_task` | Mark task as DONE with outcome |
| `comment_and_escalate` | Add comment and re-assign to another team |
| `get_task` | Fetch full task details |
| `list_tasks` | List all tasks with optional filters |

See [agents.md](./agents.md) for full documentation.
