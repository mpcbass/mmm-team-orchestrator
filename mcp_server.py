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
import chat_manager

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "mmm-team-orchestrator", "version": "1.1.0"}

TOOLS = [
    # ------------------------------------------------------------------
    # Task tools
    # ------------------------------------------------------------------
    {
        "name": "create_task",
        "description": "Create a new task and assign it to a team.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "team": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "parent_task_id": {"type": "string"},
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
                "task_id": {"type": "string"},
                "outcome": {"type": "string"},
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
                "task_id": {"type": "string"},
                "comment": {"type": "string"},
                "new_team": {"type": "string"},
            },
            "required": ["task_id", "comment", "new_team"],
        },
    },
    {
        "name": "get_task",
        "description": "Read the current state of a task by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {"task_id": {"type": "string"}},
            "required": ["task_id"],
        },
    },
    {
        "name": "list_tasks",
        "description": "List tasks, optionally filtered by team and/or status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "team": {"type": "string"},
                "status": {"type": "string", "enum": ["OPEN", "IN_PROGRESS", "DONE", "ESCALATED"]},
            },
            "required": [],
        },
    },
    # ------------------------------------------------------------------
    # Chat tools
    # ------------------------------------------------------------------
    {
        "name": "open_chat",
        "description": "Open a group chat session between multiple teams.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Chat topic/title"},
                "teams": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of team IDs participating in the chat",
                },
                "description": {"type": "string", "description": "Optional context"},
                "linked_task_id": {"type": "string", "description": "Optional task ID this chat relates to"},
            },
            "required": ["title", "teams"],
        },
    },
    {
        "name": "post_message",
        "description": "Post a message to an open group chat on behalf of a team.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chat_id": {"type": "string"},
                "author_team": {"type": "string", "description": "Team sending the message"},
                "text": {"type": "string", "description": "Message content"},
            },
            "required": ["chat_id", "author_team", "text"],
        },
    },
    {
        "name": "close_chat",
        "description": "Close a group chat session with an optional summary.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chat_id": {"type": "string"},
                "summary": {"type": "string", "description": "Optional outcome summary of the chat"},
            },
            "required": ["chat_id"],
        },
    },
    {
        "name": "get_chat",
        "description": "Read the full state of a chat including all messages.",
        "inputSchema": {
            "type": "object",
            "properties": {"chat_id": {"type": "string"}},
            "required": ["chat_id"],
        },
    },
    {
        "name": "list_chats",
        "description": "List chats, optionally filtered by team and/or status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "team": {"type": "string"},
                "status": {"type": "string", "enum": ["OPEN", "CLOSED"]},
            },
            "required": [],
        },
    },
]


def _ok(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _text(content) -> dict:
    return {"type": "text", "text": json.dumps(content, indent=2)}


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
                title=args["title"], team=args["team"],
                description=args.get("description", ""),
                priority=args.get("priority", "medium"),
                parent_task_id=args.get("parent_task_id"),
            )
        elif name == "complete_task":
            result = task_manager.complete_task(task_id=args["task_id"], outcome=args["outcome"])
        elif name == "comment_and_escalate":
            result = task_manager.comment_and_escalate(
                task_id=args["task_id"], comment=args["comment"], new_team=args["new_team"]
            )
        elif name == "get_task":
            result = task_manager.get_task(task_id=args["task_id"])
        elif name == "list_tasks":
            result = task_manager.list_tasks(team=args.get("team"), status=args.get("status"))
        elif name == "open_chat":
            result = chat_manager.open_chat(
                title=args["title"], teams=args["teams"],
                description=args.get("description", ""),
                linked_task_id=args.get("linked_task_id"),
            )
        elif name == "post_message":
            result = chat_manager.post_message(
                chat_id=args["chat_id"], author_team=args["author_team"], text=args["text"]
            )
        elif name == "close_chat":
            result = chat_manager.close_chat(chat_id=args["chat_id"], summary=args.get("summary", ""))
        elif name == "get_chat":
            result = chat_manager.get_chat(chat_id=args["chat_id"])
        elif name == "list_chats":
            result = chat_manager.list_chats(team=args.get("team"), status=args.get("status"))
        else:
            return _err(req_id, -32601, f"Unknown tool: {name}")
        return _ok(req_id, {"content": [_text(result)]})
    except (KeyError, ValueError) as e:
        return _ok(req_id, {"content": [_text({"error": str(e)})], "isError": True})
    except Exception as e:
        logger.exception("Unhandled error in tool %s", name)
        return _ok(req_id, {"content": [_text({"error": str(e)})], "isError": True})


DISPATCH = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
}


def main():
    logger.info("MMM Team Orchestrator MCP server v1.1.0 starting (stdio)")
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            req = json.loads(raw_line)
        except json.JSONDecodeError as e:
            print(json.dumps(_err(None, -32700, f"Parse error: {e}")), flush=True)
            continue
        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params", {})
        handler = DISPATCH.get(method)
        if handler is None:
            if req_id is not None:
                print(json.dumps(_err(req_id, -32601, f"Method not found: {method}")), flush=True)
            continue
        resp = handler(req_id, params)
        if req_id is not None:
            print(json.dumps(resp), flush=True)


if __name__ == "__main__":
    main()
