import os
import logging
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

try:
    import cohere
except ImportError:
    logger.warning("Cohere library not found. Please install it with: pip install cohere")


class EmbeddingService:
    """
    Service for generating embeddings using Cohere API
    """

    def __init__(self):
        """
        Initialize the embedding service with Cohere client
        """
        self.cohere_api_key = os.getenv("COHERE_API_KEY")

        if not self.cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")

        try:
            self.client = cohere.Client(self.cohere_api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Cohere client: {e}")
            raise

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Cohere API.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        logger.info(f"Generating embeddings for {len(texts)} text(s)")

        try:
            # Cohere API has rate limits, so we'll process in batches if needed
            embeddings = []

            # Process in batches to respect API limits
            batch_size = 96  # Cohere's max batch size is 96
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                response = self.client.embed(
                    texts=batch,
                    model="embed-multilingual-v3.0",  # Using the latest multilingual model
                    input_type="search_query"  # Appropriate for search queries
                )

                embeddings.extend(response.embeddings)

                logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.

        Args:
            query: The query string to embed

        Returns:
            Embedding vector (list of floats)
        """
        embeddings = self.embed_texts([query])
        return embeddings[0] if embeddings else []