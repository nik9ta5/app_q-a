# =======================
# Сервис для управления чатами
# =======================
from typing import Dict, List, Optional
import json


class ChatService:
    def __init__(self, storage: Optional[Dict] = None):
        self.storage = storage if storage is not None else {}

    def get_chat_history(self, session_id: str) -> List[Dict[str, str]]:
        # get chat history ([{}, {}, {}, ...., {}])
        history_json = self.storage.get(session_id, "[]")
        return json.loads(history_json)

    def update_chat_history(self, session_id: str, message: Dict[str, str]):
        history = self.get_chat_history(session_id)
        history.append(message)
        self.storage[session_id] = json.dumps(history)

    def clear_chat_history(self, session_id: str):
        if session_id in self.storage:
            del self.storage[session_id]