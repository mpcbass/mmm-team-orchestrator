#!/usr/bin/env python3
"""MCP server for MMM Team Orchestrator — stdio transport."""
import json
import sys
import logging
import os

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_server")

import task_manager

# ---------------------------------------------------------------------------
# MCP protocol constants
# ---------------------------------------------------------------------------
PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "mmm-team-orchestrator", "version": "1.0.0"}

TOOLS = [
    {
        "name": "create_task",
        "description": "Create a new task and assign it to a team.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short task title"},
                "team": {"type": "string", "description": "Target team ID"},
                "description": {"type": "string", "description": "Full task details"},
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Task priority (default: medium)",
                },
                "parent_task_id": {
                    "type": "string",
                    "description": "Optional parent task ID for sub-tasks",
                },
            },
            "required": ["title", "team"],
        },
    },
    {
        "name": "complete_task",
        "description": "Mark a task as DONE with an outcome summary.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID to complete"},
                "outcome": {"type": "string", "description": "What was accomplished"},
            },
            "required": ["task_id", "outcome"],
        },
    },
    {
        "name": "comment_and_escalate",
        "description": "Add a comment to a task and re-assign it to another team.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
                "comment": {"type": "string", "description": "Reason for escalation"},
                "new_team": {"type": "string", "description": "Team to escalate to"},
            },
            "required": ["task_id", "comment", "new_team"],
        },
    },
    {
        "name": "get_task",
        "description": "Read the current state of a task by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "list_tasks",
        "description": "List tasks, optionally filtered by team and/or status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "team": {"type": "string", "description": "Filter by team ID"},
                "status": {
                    "type": "string",
                    "enum": ["OPEN", "IN_PROGRESS", "DONE", "ESCALATED"],
                    "description": "Filter by status",
                },
            },
            "required": [],
        },
    },
]


# ---------------------------------------------------------------------------
# JSON-RPC helpers
# ---------------------------------------------------------------------------

def _ok(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _text(content) -> dict:
    return {"type": "text", "text": json.dumps(content, indent=2)}


# ---------------------------------------------------------------------------
# Request handlers
# ---------------------------------------------------------------------------

def handle_initialize(req_id, params):
    return _ok(req_id, {
        "protocolVersion": PROTOCOL_VERSION,
        "serverInfo": SERVER_INFO,
        "capabilities": {"tools": {}},
    })


def handle_tools_list(req_id, params):
    return _ok(req_id, {"tools": TOOLS})


def handle_tools_call(req_id, params):
    name = params.get("name")
    args = params.get("arguments", {})
    try:
        if name == "create_task":
            result = task_manager.create_task(
                title=args["title"],
                team=args["team"],
                description=args.get("description", ""),
                priority=args.get("priority", "medium"),
                parent_task_id=args.get("parent_task_id"),
            )
        elif name == "complete_task":
            result = task_manager.complete_task(
                task_id=args["task_id"],
                outcome=args["outcome"],
            )
        elif name == "comment_and_escalate":
            result = task_manager.comment_and_escalate(
                task_id=args["task_id"],
                comment=args["comment"],
                new_team=args["new_team"],
            )
        elif name == "get_task":
            result = task_manager.get_task(task_id=args["task_id"])
        elif name == "list_tasks":
            result = task_manager.list_tasks(
                team=args.get("team"),
                status=args.get("status"),
            )
        else:
            return _err(req_id, -32601, f"Unknown tool: {name}")
        return _ok(req_id, {"content": [_text(result)]})
    except KeyError as e:
        return _ok(req_id, {"content": [_text({"error": str(e)})], "isError": True})
    except ValueError as e:
        return _ok(req_id, {"content": [_text({"error": str(e)})], "isError": True})
    except Exception as e:
        logger.exception("Unhandled error in tool %s", name)
        return _ok(req_id, {"content": [_text({"error": str(e)})], "isError": True})


DISPATCH = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
}


# ---------------------------------------------------------------------------
# stdio loop
# ---------------------------------------------------------------------------

def main():
    logger.info("MMM Team Orchestrator MCP server starting (stdio)")
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            req = json.loads(raw_line)
        except json.JSONDecodeError as e:
            resp = _err(None, -32700, f"Parse error: {e}")
            print(json.dumps(resp), flush=True)
            continue

        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params", {})

        handler = DISPATCH.get(method)
        if handler is None:
            # notifications (no id) are silently ignored
            if req_id is not None:
                resp = _err(req_id, -32601, f"Method not found: {method}")
                print(json.dumps(resp), flush=True)
            continue

        resp = handler(req_id, params)
        if req_id is not None:
            print(json.dumps(resp), flush=True)


if __name__ == "__main__":
    main()
