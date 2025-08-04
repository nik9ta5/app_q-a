# =======================
# Сервис, отвечающий за управление документами
# =======================
import os
import logging
from typing import List, Optional

from services.documentService.documentLoader import DocumentLoader
from services.documentService.textSplitter import TextSplitterService
from services.VDBService.vectorDataBase import VectorDBService


class DocumentService:
    def __init__(
        self, 
        documentLoader : DocumentLoader, 
        textSplitter : TextSplitterService,
        vector_store : VectorDBService,
        logger : logging = None
        ):
        if logger:
            logger.debug("document service init start")

        self.documentLoader = documentLoader
        self.textSplitter = textSplitter
        self.vector_store = vector_store
        self.logger = logger

        if logger:
            logger.debug("document service init end")


    def load_docs(
        self,
        user_id : str,
        upload_files : List[str]
        ):
        """method for load docs"""
        try:
            all_docs = self.documentLoader.load_documents(user_id, upload_files)
            all_split_docs = self.textSplitter.split_documents(all_docs)
            self.vector_store.insert(all_split_docs)
        except Exception as e:
            raise Exception(e)