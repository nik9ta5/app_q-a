from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class TextSplitterService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
    
    def split_documents(self, documents: List[Dict]) -> List[Document]:
        all_chunks = []
        for doc in documents:
            text = doc["content"]
            metadata = doc["metadata"]
            
            chunks = self.splitter.split_text(text)
            
            # Создаем объекты Document для каждого чанка
            for chunk_text in chunks:
                all_chunks.append(
                    Document(page_content=chunk_text, metadata=metadata)
                )
        return all_chunks