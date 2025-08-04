# =======================
# Сервис для работы с промптами
# =======================
import logging
from langchain_core.documents import Document

class PromptService:
    def __init__(
        self, 
        instruction : str, 
        system_instruction : str = None,
        logger : logging = None
        ):
        if logger:
            logger.debug("prompt service init start")
        self.logger = logger
        self.instruction = instruction
        self.system_instruction = system_instruction

        if logger:
            logger.debug("prompt service init end")


    def create_rag_prompt(self, query: str, documents: list[Document], chat_history: list[dict]):        
        context = "\n".join([item.page_content for item in documents])
        
        chat_history_str = '\n'.join([f"{item['role']}: {item['content']}" for item in chat_history])

        # RAG Prompt template
        prompt_template = """
### Instruction
{instruction}

### Chat History
{chat_history_str}

### Context
{context}

### User Question
{query}

### Answer
"""
        prompt = prompt_template.format(
            instruction=self.instruction,
            chat_history_str=chat_history_str,
            context=context,
            query=query
        )

        if self.system_instruction:
            prompt = f"{self.system_instruction}\n" + prompt
            
        if self.logger:
            self.logger.debug(f"========= [PROMPT_SERVICE] START PROMP =========\n\n\n---{prompt}---\n\n\n========= END PROMP =========\n")

        return prompt