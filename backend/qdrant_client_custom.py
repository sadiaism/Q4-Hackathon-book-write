import os
import uuid
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct, Distance, VectorParams
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

load_dotenv()

class QdrantManager:
    def __init__(self):
        # Initialize Qdrant client
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "book_embeddings")

        if self.qdrant_url and self.qdrant_api_key:
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
                prefer_grpc=True
            )
        else:
            # For local development
            self.client = QdrantClient(host="localhost", port=6333)

        # Initialize sentence transformer model for embeddings
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

        # Create collection if it doesn't exist
        self._create_collection()

    def _create_collection(self):
        """
        Create Qdrant collection for book embeddings if it doesn't exist
        """
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
        except:
            # Create collection with vector size 384 (for all-MiniLM-L6-v2)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def add_text_chunks(self, chunks: List[Dict], book_id: str = None) -> bool:
        """
        Add text chunks to Qdrant collection

        Args:
            chunks: List of dictionaries with 'text', 'chunk_id', and optional metadata
            book_id: Optional book identifier to group chunks
        """
        try:
            points = []
            for chunk in chunks:
                # Generate embedding for the text
                embedding = self.encoder.encode(chunk['text']).tolist()

                # Create point structure
                point = PointStruct(
                    id=chunk.get('chunk_id', str(uuid.uuid4())),
                    vector=embedding,
                    payload={
                        "text": chunk['text'],
                        "book_id": book_id or chunk.get('book_id', ''),
                        "metadata": chunk.get('metadata', {}),
                        "source": chunk.get('source', 'unknown')
                    }
                )
                points.append(point)

            # Upload points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            return True
        except Exception as e:
            print(f"Error adding text chunks to Qdrant: {e}")
            return False

    def search_similar_texts(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for similar texts in the Qdrant collection

        Args:
            query: Query text to search for
            limit: Number of similar texts to return

        Returns:
            List of dictionaries containing similar texts and their metadata
        """
        try:
            query_embedding = self.encoder.encode(query).tolist()

            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )

            results = []
            for hit in hits:
                result = {
                    "id": hit.id,
                    "text": hit.payload.get("text", ""),
                    "book_id": hit.payload.get("book_id", ""),
                    "metadata": hit.payload.get("metadata", {}),
                    "source": hit.payload.get("source", ""),
                    "score": hit.score
                }
                results.append(result)

            return results
        except Exception as e:
            print(f"Error searching in Qdrant: {e}")
            return []

    def delete_collection(self):
        """
        Delete the entire collection (use with caution)
        """
        try:
            self.client.delete_collection(self.collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False

    def get_collection_info(self):
        """
        Get information about the collection
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.vectors.size,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "points_count": collection_info.points_count
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return None

# Global instance
qdrant_manager = QdrantManager()