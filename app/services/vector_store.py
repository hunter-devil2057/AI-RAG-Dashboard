from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from app.core.config import settings
from typing import List, Dict, Any
import uuid

class VectorStore:
    def __init__(self):
        try:
            # Try to connect to the Qdrant server
            self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=5)
            # Test connection
            self.client.get_collections()
            print(f"Connected to Qdrant server at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        except Exception as e:
            print(f"Qdrant server unreachable ({e}). Falling back to local storage at ./qdrant_data")
            # Fallback to local storage
            self.client = QdrantClient(path="./qdrant_data")
            
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        
        # Initialize collection if not exists
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # text-embedding-3-small is 1536 dims
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            )

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = self.openai_client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        return [data.embedding for data in response.data]

    def upsert_chunks(self, chunks: List[str], metadata: Dict[str, Any]):
        if not chunks:
            return
        
        embeddings = self.get_embeddings(chunks)
        
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_metadata = metadata.copy()
            point_metadata["text"] = chunk
            point_metadata["chunk_index"] = i
            
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=point_metadata
            ))
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_vector = self.get_embeddings([query])[0]
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )
        
        return [res.payload for res in results]

vector_store = VectorStore()
