import os
import logging
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.conversions import common_types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class QdrantService:
    """
    Service for interacting with Qdrant vector database
    """

    def __init__(self, collection_name: str = "rag_embedding"):
        """
        Initialize the Qdrant service with client and collection name
        """
        self.collection_name = collection_name
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")

        # Initialize Qdrant client
        if self.qdrant_url and self.qdrant_api_key:
            self.client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
        elif self.qdrant_url:
            self.client = QdrantClient(url=self.qdrant_url)
        else:
            # Use local Qdrant instance
            self.client = QdrantClient(host="localhost", port=6333)

        # Create collection if it doesn't exist
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        """
        Create the Qdrant collection if it doesn't already exist
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            existing_collections = [col.name for col in collections.collections]

            if self.collection_name in existing_collections:
                logger.info(f"Collection {self.collection_name} already exists")
                return

            # Create new collection
            # Cohere's embed-multilingual-v3.0 produces 1024-dimensional vectors
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
            )

            logger.info(f"Successfully created collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Error creating collection {self.collection_name}: {e}")
            raise

    def search(self, query_vector: List[float], limit: int = 5) -> List[models.ScoredPoint]:
        """
        Search for similar vectors in the Qdrant collection.

        Args:
            query_vector: The query vector to search for
            limit: Maximum number of results to return

        Returns:
            List of scored points (matches)
        """
        logger.info(f"Searching for similar vectors in collection: {self.collection_name}")

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )

            logger.info(f"Found {len(results)} similar vectors")
            return results

        except Exception as e:
            logger.error(f"Error searching in Qdrant: {e}")
            raise

    def retrieve_by_ids(self, ids: List[str]) -> List[models.Record]:
        """
        Retrieve specific records by their IDs from the Qdrant collection.

        Args:
            ids: List of record IDs to retrieve

        Returns:
            List of records
        """
        logger.info(f"Retrieving records by IDs from collection: {self.collection_name}")

        try:
            records = self.client.retrieve(
                collection_name=self.collection_name,
                ids=ids
            )

            logger.info(f"Retrieved {len(records)} records by IDs")
            return records

        except Exception as e:
            logger.error(f"Error retrieving records by IDs from Qdrant: {e}")
            raise