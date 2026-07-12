import logging
from typing import Optional, List
from models import Chat, ChatMessage
from storage import save_chat, load_chat, list_chats as storage_list_chats
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def open_chat(
    title: str,
    teams: List[str],
    description: str = "",
    linked_task_id: Optional[str] = None,
) -> dict:
    if not title.strip():
        raise ValueError("title cannot be empty")
    if not teams:
        raise ValueError("at least one team is required")
    chat = Chat(
        title=title.strip(),
        teams=[t.strip() for t in teams if t.strip()],
        description=description,
        linked_task_id=linked_task_id,
    )
    save_chat(chat)
    logger.info("Opened chat %s with teams %s", chat.chat_id, chat.teams)
    return chat.to_dict()


def post_message(
    chat_id: str,
    author_team: str,
    text: str,
) -> dict:
    if not text.strip():
        raise ValueError("text cannot be empty")
    if not author_team.strip():
        raise ValueError("author_team cannot be empty")
    chat = load_chat(chat_id)
    if chat is None:
        raise KeyError(f"Chat {chat_id} not found")
    if chat.status == "CLOSED":
        raise ValueError(f"Chat {chat_id} is closed")
    msg = ChatMessage(
        timestamp=datetime.now(timezone.utc).isoformat(),
        author_team=author_team.strip(),
        text=text.strip(),
    )
    chat.messages.append(msg)
    chat.touch()
    save_chat(chat)
    logger.info("Message posted to chat %s by %s", chat_id, author_team)
    return chat.to_dict()


def close_chat(chat_id: str, summary: str = "") -> dict:
    chat = load_chat(chat_id)
    if chat is None:
        raise KeyError(f"Chat {chat_id} not found")
    if chat.status == "CLOSED":
        raise ValueError(f"Chat {chat_id} is already closed")
    chat.status = "CLOSED"
    chat.summary = summary.strip()
    chat.touch()
    save_chat(chat)
    logger.info("Closed chat %s", chat_id)
    return chat.to_dict()


def get_chat(chat_id: str) -> dict:
    chat = load_chat(chat_id)
    if chat is None:
        raise KeyError(f"Chat {chat_id} not found")
    return chat.to_dict()


def list_chats(team: Optional[str] = None, status: Optional[str] = None) -> list:
    return storage_list_chats(team=team, status=status)
