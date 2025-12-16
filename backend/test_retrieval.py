"""
Main retrieval testing framework for RAG pipeline validation
"""
import os
import time
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
import cohere
from test_config import (
    QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME,
    COHERE_API_KEY, DEFAULT_TOP_K, QUERY_TIMEOUT
)
from validation_utils import (
    validate_content_accuracy, validate_metadata,
    format_test_result, clean_json_output
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RetrievalTester:
    def __init__(self):
        """Initialize the retrieval testing framework with Qdrant and Cohere clients."""
        # Initialize Cohere client
        if not COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")
        self.cohere_client = cohere.Client(COHERE_API_KEY)

        # Initialize Qdrant client
        if QDRANT_URL and QDRANT_API_KEY:
            self.qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=QUERY_TIMEOUT)
        elif QDRANT_URL:
            self.qdrant_client = QdrantClient(url=QDRANT_URL, timeout=QUERY_TIMEOUT)
        else:
            # Use local Qdrant instance
            self.qdrant_client = QdrantClient(host="localhost", port=6333, timeout=QUERY_TIMEOUT)

        self.collection_name = QDRANT_COLLECTION_NAME

    def connect_to_qdrant(self) -> bool:
        """
        Connect to existing Qdrant collection and verify accessibility.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to get collection info to verify it exists and is accessible
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            logger.info(f"Successfully connected to Qdrant collection: {self.collection_name}")
            logger.info(f"Collection vectors count: {collection_info.points_count}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant collection {self.collection_name}: {e}")
            return False

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a sample query using Cohere.

        Args:
            query: Query text to embed

        Returns:
            Embedding vector as a list of floats
        """
        try:
            response = self.cohere_client.embed(
                texts=[query],
                model="embed-multilingual-v3.0",  # Using the same model as in ingestion
                input_type="search_query"  # Appropriate for search queries
            )
            embedding = response.embeddings[0]
            logger.info(f"Generated embedding for query: '{query[:50]}...'")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding for query '{query}': {e}")
            raise

    def query_qdrant_with_topk(self, query_embedding: List[float], top_k: int = DEFAULT_TOP_K) -> List[Dict[str, Any]]:
        """
        Query Qdrant with top-k search.

        Args:
            query_embedding: Embedding vector to search for
            top_k: Number of top matches to retrieve

        Returns:
            List of retrieved results with text, metadata, and scores
        """
        try:
            # Perform search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,  # Include metadata
                with_vectors=False   # Don't need the vectors for validation
            )

            # Format results
            formatted_results = []
            for result in search_results:
                formatted_result = {
                    "id": result.id,
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "url": result.payload.get("url", ""),
                    "chunk_id": result.payload.get("chunk_index", result.payload.get("chunk_id", -1))
                }
                formatted_results.append(formatted_result)

            logger.info(f"Retrieved {len(formatted_results)} results for top-{top_k} search")
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to query Qdrant: {e}")
            raise

    def validate_retrieved_chunks(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that retrieved chunks match original text where possible.

        Args:
            results: List of retrieved results from Qdrant

        Returns:
            Validation results dictionary
        """
        total_chunks = len(results)
        accurate_chunks = 0
        validation_details = []

        for result in results:
            # For now, we'll consider this a basic validation
            # In a real scenario, we'd have the original text to compare against
            text = result.get("text", "")
            if len(text) > 0:
                # If we had original text to compare, we would do that here
                # For now, just validate that text exists and has content
                is_accurate = len(text.strip()) > 0
                if is_accurate:
                    accurate_chunks += 1

                validation_details.append({
                    "id": result["id"],
                    "has_content": is_accurate,
                    "text_length": len(text)
                })
            else:
                validation_details.append({
                    "id": result["id"],
                    "has_content": False,
                    "text_length": 0
                })

        accuracy_rate = accurate_chunks / total_chunks if total_chunks > 0 else 0

        return {
            "total_chunks": total_chunks,
            "accurate_chunks": accurate_chunks,
            "accuracy_rate": accuracy_rate,
            "validation_details": validation_details,
            "overall_accuracy_pass": accuracy_rate >= 0.9  # 90% threshold
        }

    def verify_metadata_correctness(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify that metadata (url, chunk_id) is returned correctly.

        Args:
            results: List of retrieved results from Qdrant

        Returns:
            Metadata validation results
        """
        total_results = len(results)
        valid_metadata_count = 0
        metadata_details = []

        for result in results:
            metadata_validation = validate_metadata({
                "url": result.get("url", ""),
                "chunk_id": result.get("chunk_id", -1)
            })

            is_valid = metadata_validation["metadata_correct"]
            if is_valid:
                valid_metadata_count += 1

            metadata_details.append({
                "id": result["id"],
                "metadata_validation": metadata_validation
            })

        validity_rate = valid_metadata_count / total_results if total_results > 0 else 0

        return {
            "total_results": total_results,
            "valid_metadata_count": valid_metadata_count,
            "validity_rate": validity_rate,
            "metadata_details": metadata_details,
            "overall_validity_pass": validity_rate >= 0.9  # 90% threshold
        }

    def basic_retrieval_test(self, query: str, top_k: int = DEFAULT_TOP_K) -> Dict[str, Any]:
        """
        Perform a basic retrieval test to check top-k match accuracy.

        Args:
            query: Query text to test
            top_k: Number of results to retrieve

        Returns:
            Test result with validation
        """
        logger.info(f"Starting basic retrieval test for query: '{query}'")
        start_time = time.time()

        try:
            # Generate embedding for query
            query_embedding = self.generate_query_embedding(query)

            # Query Qdrant
            results = self.query_qdrant_with_topk(query_embedding, top_k)

            # Validate retrieved chunks
            chunk_validation = self.validate_retrieved_chunks(results)

            # Validate metadata
            metadata_validation = self.verify_metadata_correctness(results)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Overall test result
            overall_pass = (
                chunk_validation["overall_accuracy_pass"] and
                metadata_validation["overall_validity_pass"] and
                execution_time < 2.0  # Less than 2 seconds
            )

            test_result = {
                "query": query,
                "top_k": top_k,
                "execution_time": execution_time,
                "overall_pass": overall_pass,
                "chunk_validation": chunk_validation,
                "metadata_validation": metadata_validation,
                "retrieved_results": results
            }

            logger.info(f"Basic retrieval test completed. Overall pass: {overall_pass}, Time: {execution_time:.2f}s")
            return test_result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Basic retrieval test failed: {e}")
            return {
                "query": query,
                "top_k": top_k,
                "execution_time": execution_time,
                "overall_pass": False,
                "error": str(e),
                "retrieved_results": []
            }

    def metadata_validation_test(self, query: str, top_k: int = DEFAULT_TOP_K) -> Dict[str, Any]:
        """
        Perform a metadata validation test.

        Args:
            query: Query text to test
            top_k: Number of results to retrieve

        Returns:
            Metadata validation test result
        """
        logger.info(f"Starting metadata validation test for query: '{query}'")
        start_time = time.time()

        try:
            # Generate embedding for query
            query_embedding = self.generate_query_embedding(query)

            # Query Qdrant
            results = self.query_qdrant_with_topk(query_embedding, top_k)

            # Validate metadata specifically
            metadata_validation = self.verify_metadata_correctness(results)

            # Calculate execution time
            execution_time = time.time() - start_time

            test_result = {
                "query": query,
                "top_k": top_k,
                "execution_time": execution_time,
                "metadata_validation": metadata_validation,
                "retrieved_results": results
            }

            logger.info(f"Metadata validation test completed in {execution_time:.2f}s")
            return test_result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Metadata validation test failed: {e}")
            return {
                "query": query,
                "top_k": top_k,
                "execution_time": execution_time,
                "error": str(e),
                "retrieved_results": []
            }

    def end_to_end_retrieval_test(self, query: str, top_k: int = DEFAULT_TOP_K) -> str:
        """
        Perform complete end-to-end retrieval test and return clean JSON output.

        Args:
            query: Query text to test
            top_k: Number of results to retrieve

        Returns:
            Clean JSON formatted test result
        """
        logger.info(f"Starting end-to-end retrieval test for query: '{query}'")
        start_time = time.time()

        try:
            # Generate embedding for query
            query_embedding = self.generate_query_embedding(query)

            # Query Qdrant
            results = self.query_qdrant_with_topk(query_embedding, top_k)

            # Validate retrieved chunks
            chunk_validation = self.validate_retrieved_chunks(results)

            # Validate metadata
            metadata_validation = self.verify_metadata_correctness(results)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Create validation summary
            validation = {
                "chunk_validation": chunk_validation,
                "metadata_validation": metadata_validation,
                "overall_pass": (
                    chunk_validation["overall_accuracy_pass"] and
                    metadata_validation["overall_validity_pass"] and
                    execution_time < 2.0
                )
            }

            # Format the result
            formatted_result = format_test_result(query, results, validation, execution_time)

            # Convert to clean JSON
            json_output = clean_json_output(formatted_result)

            logger.info(f"End-to-end test completed successfully in {execution_time:.2f}s")
            return json_output

        except Exception as e:
            execution_time = time.time() - start_time
            error_result = {
                "query": query,
                "execution_time": execution_time,
                "error": str(e),
                "overall_pass": False,
                "results": [],
                "total_results": 0
            }
            logger.error(f"End-to-end test failed: {e}")
            return clean_json_output(error_result)


def run_sample_tests():
    """
    Run sample tests to demonstrate the retrieval testing framework.
    """
    logger.info("Starting retrieval testing framework demonstration")

    try:
        # Initialize the tester
        tester = RetrievalTester()

        # Verify connection to Qdrant
        if not tester.connect_to_qdrant():
            logger.error("Cannot proceed without Qdrant connection")
            return

        # Sample queries for testing
        sample_queries = [
            "What is the main concept of Physical AI?",
            "Explain humanoid robotics applications",
            "How does machine learning apply to robotics?",
            "What are the key challenges in AI robotics?"
        ]

        # Run basic retrieval tests
        logger.info("\n--- Running Basic Retrieval Tests ---")
        for i, query in enumerate(sample_queries, 1):
            logger.info(f"\nTest {i}: '{query}'")
            result = tester.basic_retrieval_test(query)
            logger.info(f"  Overall Pass: {result['overall_pass']}")
            logger.info(f"  Execution Time: {result['execution_time']:.2f}s")
            logger.info(f"  Results Retrieved: {len(result['retrieved_results'])}")

        # Run metadata validation tests
        logger.info("\n--- Running Metadata Validation Tests ---")
        for i, query in enumerate(sample_queries[:2], 1):  # Just first 2 for metadata test
            logger.info(f"\nMetadata Test {i}: '{query}'")
            result = tester.metadata_validation_test(query)
            logger.info(f"  Validity Rate: {result['metadata_validation']['validity_rate']:.2f}")
            logger.info(f"  Results Retrieved: {len(result['retrieved_results'])}")

        # Run end-to-end tests with clean JSON output
        logger.info("\n--- Running End-to-End Tests with Clean JSON Output ---")
        for i, query in enumerate(sample_queries[:1], 1):  # Just first one for full output
            logger.info(f"\nEnd-to-End Test {i}: '{query}'")
            json_result = tester.end_to_end_retrieval_test(query)
            logger.info(f"  JSON Output Preview: {json_result[:200]}...")

        logger.info("\n--- All Tests Completed ---")

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise


if __name__ == "__main__":
    run_sample_tests()