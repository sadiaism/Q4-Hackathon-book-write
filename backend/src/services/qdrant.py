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

    def upsert_vectors(self, texts: List[str], urls: List[str], metadata_list: Optional[List[dict]] = None, ids: Optional[List[str]] = None) -> bool:
        """
        Upsert (add/update) vectors to the Qdrant collection.

        Args:
            texts: List of text chunks to embed and store
            urls: List of URLs corresponding to each text chunk
            metadata_list: Optional list of metadata dictionaries for each text chunk
            ids: Optional list of IDs for the vectors (if not provided, Qdrant will generate them)

        Returns:
            True if upsert operation was successful
        """
        logger.info(f"Upserting {len(texts)} vectors to collection: {self.collection_name}")

        try:
            # Generate IDs if not provided
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in range(len(texts))]

            # Prepare payloads
            payloads = []
            for i, text in enumerate(texts):
                payload = {
                    "text": text,
                    "url": urls[i] if i < len(urls) else "",
                    "chunk_index": i
                }

                # Add additional metadata if provided
                if metadata_list and i < len(metadata_list):
                    payload.update(metadata_list[i])

                payloads.append(payload)

            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=models.Batch(
                    ids=ids,
                    vectors=[None] * len(texts),  # Vectors will be populated by embedding service
                    payloads=payloads
                )
            )

            logger.info(f"Successfully upserted {len(texts)} vectors to collection: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error upserting vectors to Qdrant: {e}")
            raise

    def update_vectors(self, embeddings: List[List[float]], ids: List[str]) -> bool:
        """
        Update the vector embeddings for existing points in the Qdrant collection.

        Args:
            embeddings: List of embedding vectors to update
            ids: List of IDs corresponding to the vectors to update

        Returns:
            True if update operation was successful
        """
        logger.info(f"Updating {len(embeddings)} vectors in collection: {self.collection_name}")

        try:
            # Update vectors in Qdrant
            self.client.update_vectors(
                collection_name=self.collection_name,
                points_updates=[
                    models.PointVectors(
                        id=ids[i],
                        vector=embeddings[i]
                    )
                    for i in range(len(embeddings))
                ]
            )

            logger.info(f"Successfully updated {len(embeddings)} vectors in collection: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error updating vectors in Qdrant: {e}")
            raise

    def get_all_points_count(self) -> int:
        """
        Get the total number of points in the collection.

        Returns:
            Total number of points in the collection
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return 0

    def search_with_payload_filter(self, query_vector: List[float], filter_payload: dict = None, limit: int = 5) -> List[models.ScoredPoint]:
        """
        Search for similar vectors in the Qdrant collection with payload filtering.

        Args:
            query_vector: The query vector to search for
            filter_payload: Optional payload filter to narrow down search
            limit: Maximum number of results to return

        Returns:
            List of scored points (matches)
        """
        logger.info(f"Searching for similar vectors in collection: {self.collection_name} with filter")

        try:
            search_filter = None
            if filter_payload:
                conditions = []
                for key, value in filter_payload.items():
                    conditions.append(models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    ))
                if conditions:
                    search_filter = models.Filter(must=conditions)

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=search_filter,
                limit=limit
            )

            logger.info(f"Found {len(results)} similar vectors with filter")
            return results

        except Exception as e:
            logger.error(f"Error searching in Qdrant with filter: {e}")
            raise

    