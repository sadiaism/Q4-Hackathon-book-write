import os
import logging
from typing import List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

from ..models.query import QueryRequest, QueryVector, RetrievedChunk, ResponseObject
from .embedding import EmbeddingService
from .qdrant import QdrantService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Configure Google Generative AI
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
else:
    logger.warning("GEMINI_API_KEY environment variable is not set")


class RAGAgentService:
    """
    Service for the RAG (Retrieval-Augmented Generation) agent
    """

    def __init__(self, collection_name: str = "rag_embedding"):
        """
        Initialize the RAG agent service with dependencies
        """
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService(collection_name)

        # Initialize the generative model
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise

    def process_query(self, query_request: QueryRequest) -> ResponseObject:
        """
        Process a query request through the RAG workflow.

        Args:
            query_request: The query request containing the user's question

        Returns:
            ResponseObject containing the answer, sources, and matched chunks
        """
        logger.info(f"Processing query: {query_request.query}")

        try:
            # Step 1: Generate embedding for the query
            query_embedding = self.embedding_service.embed_query(query_request.query)
            logger.info("Generated query embedding")

            # Step 2: Search for similar vectors in Qdrant
            search_results = self.qdrant_service.search(query_embedding, limit=5)
            logger.info(f"Found {len(search_results)} similar vectors")

            # Step 3: Extract matched chunks from search results
            matched_chunks = []
            sources = set()

            for result in search_results:
                if result.payload:
                    chunk = RetrievedChunk(
                        content=result.payload.get("text", ""),
                        source=result.payload.get("url", ""),
                        score=result.score,
                        metadata=result.payload.get("metadata", {})
                    )
                    matched_chunks.append(chunk)
                    sources.add(result.payload.get("url", ""))

            logger.info(f"Extracted {len(matched_chunks)} matched chunks")

            # Step 4: Generate answer using the matched chunks as context
            answer = self._generate_answer(query_request.query, matched_chunks)
            logger.info("Generated answer")

            # Step 5: Create and return response object
            response = ResponseObject(
                answer=answer,
                sources=list(sources),
                matched_chunks=matched_chunks,
                query_id=None  # In a real implementation, you might want to generate a unique ID
            )

            logger.info("Query processing completed successfully")
            return response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise

    def _generate_answer(self, query: str, matched_chunks: List[RetrievedChunk]) -> str:
        """
        Generate an answer using the query and matched chunks as context.

        Args:
            query: The original user query
            matched_chunks: List of retrieved chunks to use as context

        Returns:
            Generated answer string
        """
        logger.info("Generating answer using Gemini model")

        try:
            # Prepare context from matched chunks
            context = "\n\n".join([f"Source: {chunk.source}\nContent: {chunk.content}" for chunk in matched_chunks])

            logger.info(f"Context length: {len(context)} characters")
            logger.info(f"Number of chunks: {len(matched_chunks)}")

            # Create prompt for the generative model
            prompt = f"""
            Based on the following context, please answer the question. If the context doesn't contain enough information to answer the question, please say so.

            Context:
            {context}

            Question: {query}

            Answer:
            """

            logger.info(f"Prompt length: {len(prompt)} characters")

            # Generate content using the Gemini model
            response = self.model.generate_content(prompt)

            logger.info(f"Raw response received: {response}")

            # Extract the text from the response
            answer = response.text if response.text else "I couldn't find a relevant answer based on the provided context."

            logger.info("Successfully generated answer")
            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return "Sorry, I encountered an error while generating the answer."

    def validate_query(self, query_request: QueryRequest) -> bool:
        """
        Validate the query request.

        Args:
            query_request: The query request to validate

        Returns:
            True if valid, False otherwise
        """
        return query_request.is_valid