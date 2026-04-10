import chromadb
from chromadb.utils import embedding_functions
import hashlib
from pathlib import Path

class MemorySystem:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="data/chromadb")
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collections = {}
    
    def _get_collection(self, user_id, shared=False):
        key = "shared" if shared else str(user_id)
        if key not in self.collections:
            self.collections[key] = self.client.get_or_create_collection(
                name=f"memory_{key}",
                embedding_function=self.embed_fn
            )
        return self.collections[key]
    
    def add_message(self, user_id, message, response, shared=False):
        coll = self._get_collection(user_id, shared)
        doc_id = hashlib.md5(f"{message}{response}".encode()).hexdigest()
        coll.upsert(
            ids=[doc_id],
            documents=[f"User: {message}\nAssistant: {response}"],
            metadatas=[{"user_id": str(user_id)}]
        )
    
    def search_history(self, user_id, query, shared=False, n_results=5):
        coll = self._get_collection(user_id, shared)
        results = coll.query(query_texts=[query], n_results=n_results)
        return results["documents"][0] if results["documents"] else []