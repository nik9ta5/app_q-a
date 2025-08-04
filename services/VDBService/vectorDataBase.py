# =======================
# Сервис, отвечающий за взаимодействие с VDB
# =======================
import uuid
import logging
from typing import List, Dict, Tuple
from langchain_chroma import Chroma
from langchain_core.documents import Document

from services.embeddingService.embeddingService import EmbeddingFunction


class VectorDBService:
    def __init__(
        self,
        persist_directory : str,
        collection_name : str,
        embedding_function : EmbeddingFunction,
        logger : logging = None
        ):
        try:
            if logger:
                logger.debug(f"vdb init start")

            self.logger = logger
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                collection_name=collection_name,
                embedding_function=embedding_function
            )
        except Exception as e:
            raise
        finally: 
            if logger:
                logger.debug(f"vdb init end")


    def find(self, text: str, user_id : str = None, k: int = 5) -> List[Document]:
        """
        Ищет k релевантных документов для данного запроса.
        
        Args:
            text (str): Текст запроса.
            k (int): Количество возвращаемых документов.

        Returns:
            List[Document]: Список найденных объектов Document.
        """
        if user_id:
            search_filter = {"user_id": user_id}
            found_docs = self.vector_store.similarity_search(
                query=text, 
                filter=search_filter,
                k=k
            )
        else:
            found_docs = self.vector_store.similarity_search(
                query=text, 
                k=k
            )
        return found_docs
    

    def insert(self, documents: List[Document]):
        """
        Функция для добавления списка документов в базу.
        Использует пакетную вставку для эффективности.
        
        Args:
            documents (List[Document]): Список объектов Document для вставки.
        """
        if not documents:
            print("No documents to insert.")
            return

        # Генерируем уникальные ID для каждого документа
        doc_ids = [str(uuid.uuid4()) for _ in range(len(documents))]

        try:
            self.vector_store.add_documents(documents=documents, ids=doc_ids)
        except Exception as e:
            raise