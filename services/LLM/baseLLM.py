# =======================
# Интерфейс для LLM
# =======================
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt : str, max_length : int, max_new_tokens : int) -> str:
        """method for generate response LLM"""
        pass