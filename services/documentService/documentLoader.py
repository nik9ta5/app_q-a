# =======================
# Сервис, отвечающий за загрузку документов
# =======================
from typing import List, Dict
import os
from langchain.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader


class DocumentLoader:
    def __init__(self):
        pass

    def load_documents(self, user_id : str, filepaths : List[str]) -> List[Dict]:
        all_documents = []
        for filepath in filepaths:
            if filepath.endswith(".pdf"):
                loader = PyMuPDFLoader(filepath)
            elif filepath.endswith(".docx"):
                loader = Docx2txtLoader(filepath)
            elif filepath.endswith(".txt"):
                loader = TextLoader(filepath)
            else:
                continue
            
            try:
                documents = loader.load()
                for doc in documents:
                    all_documents.append({
                        "content": doc.page_content,
                        "metadata": {
                            **doc.metadata, 
                            "source_file": filepath, 
                            "user_id" : user_id}
                    })  
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
                raise Exception(e)
        print(all_documents)
        return all_documents