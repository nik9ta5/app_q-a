# =======================
# RAG-service, реализация RAG пайплайна
# =======================
from services.LLM.baseLLM import BaseLLM
from services.promptService.promptService import PromptService
from services.chatService.chatService import ChatService
from services.VDBService.vectorDataBase import VectorDBService
import logging
from langchain_core.documents import Document
from typing import List, Dict, Tuple

class RAGService:
    def __init__(self, 
        llm : BaseLLM, 
        promptService : PromptService,
        chatService : ChatService,
        vector_db : VectorDBService,
        logger : logging = None
        ):

        if logger:
            logger.debug(f"rag service init start")

        self.llm = llm
        self.promptService = promptService
        self.chatService = chatService
        self.vector_db = vector_db
        self.logger = logger

        if logger:
            logger.debug(f"rag service init end")


    def response(
        self, 
        query : str, 
        session_id : str,
        max_length : int = 1024,
        max_new_tokens : int = 256,
        k : int = 3
        ) -> Tuple[str, List[Document]]:
        """method for RAG response"""
        # === GET CHAT HISTORY ===
        chat_history = self.chatService.get_chat_history(session_id)

        if self.logger:
            chat_history_str = "".join([item['role'] + ": " + item['content'] for item in chat_history])
            self.logger.debug(f"========= [RAG_SERVICE] START CHAT HISTORY =========\n\n\n---{chat_history_str}---\n\n\n========= END CHAT HISTORY =========\n")

        # === FIND DOCS ===
        relevant_docs = self.vector_db.find(query, user_id=session_id, k=k)

        if self.logger:
            self.logger.debug(f"========= [RAG_SERVICE] START VDB SELECT =========\n\n\n---{relevant_docs}---\n\n\n========= END VDB SELECT =========\n")


        # === CREATE PROMPT ===
        prompt_for_model = self.promptService.create_rag_prompt(query, relevant_docs, chat_history)

        if self.logger:
            self.logger.debug(f"========= [RAG_SERVICE] START PROMP =========\n\n\n---{prompt_for_model}---\n\n\n========= END PROMP =========\n")


        # === LLM ANSWER GEENRATE ===
        model_response = self.llm.generate(
            prompt_for_model, 
            max_length=max_length, 
            max_new_tokens=max_new_tokens,
            repetition_penalty=1.5,
            no_repeat_ngram_size=3,
            do_sample=True, #False - use greedy search tokens 
            top_k=50,
            top_p=0.9, #find set tokens sum probability >= top_p
            temperature=0.4
        )

        split_answer_model = model_response.split("### Answer\n")[-1]
        if self.logger:
            self.logger.debug(f"======== [SPLIR ANSWER MODEL] ========{split_answer_model}======== [SPLIR ANSWER MODEL] ========")
        # === CHECK LLM ANSWER, SPLIT ANSWER ===
        # maybe later
        # model_response

        if self.logger:
            self.logger.debug(f"========= [RAG_SERVICE] START MODEL RESPONSE =========\n\n\n---{model_response}---\n\n\n========= END MODEL RESPONSE =========\n")

        
        # === UPDATE CHAT HISTORY ===
        self.chatService.update_chat_history(session_id, {"role" : "user", "content" : query})
        self.chatService.update_chat_history(session_id, {"role" : "assistent", "content" : split_answer_model})
        #return split answer (without prompt)
        return split_answer_model, relevant_docs