"""In-process conversation memory keyed by session_id.

For a real deployment we would persist to Redis or Postgres. For a college
demo, in-memory is fine and keeps setup zero-config.
"""
from collections import defaultdict, deque
from threading import Lock
from app.models.schemas import ChatMessage


class ConversationMemory:
    def __init__(self, max_turns_per_session: int = 20):
        self._store: dict[str, deque[ChatMessage]] = defaultdict(
            lambda: deque(maxlen=max_turns_per_session * 2)
        )
        self._lock = Lock()

    def append(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            self._store[session_id].append(ChatMessage(role=role, content=content))

    def history(self, session_id: str) -> list[ChatMessage]:
        with self._lock:
            return list(self._store[session_id])

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._store.pop(session_id, None)
