from langchain_core.documents import Document
from chromadb import EmbeddingFunction, Documents, Embeddings
from sentence_transformers import SentenceTransformer

# ---------- Класс для эмбеддинг функции ----------

class SentenceTransformerEmbedding(EmbeddingFunction):
    def __init__(self, 
        model_name='sentence-transformers/all-MiniLM-L6-v2', 
        cache_folder=None, 
        flull_path = None
        ):
        
        if flull_path:
            self.embed_model = SentenceTransformer(flull_path)
        else:
            self.embed_model = SentenceTransformer(
                model_name, 
                cache_folder=cache_folder
            )
    
    def embed_documents(self, texts):
        """ Создать эмбеддинги для переданных текстов """
        return [self.embed_model.encode(item) for item in texts]
    
    def embed_query(self, query):
        """method for create embedding"""
        return self.embed_model.encode(query)

    def __call__(self, input: Document) -> Embeddings:
        return self.embed_model.encode(input.page_content)
    
    def __call__(self, input: Documents) -> Embeddings:
        return [self.embed_model.encode(item.page_content) for item in input]
    

if __name__ == "__main__":
    pass
    # vector_store = Chroma(
    #     collection_name="foo",
    #     embedding_function=SentenceTransformerEmbedding()
    # )

    # document_9 = Document(
    #     page_content="The stock market is down 500 points today due to fears of a recession.",
    #     metadata={"source": "news"},
    #     id=9,
    # )