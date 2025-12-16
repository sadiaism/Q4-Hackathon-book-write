import pytest
import os
import sys
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import from backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from src.models.query import QueryRequest
from src.services.rag_agent import RAGAgentService

# Create test client
client = TestClient(app)


class TestRAGAgent:
    """Test cases for the RAG Agent functionality"""

    def test_ask_endpoint_valid_query(self):
        """Test that the ask endpoint returns a valid response for a valid query"""
        # Mock the RAG agent service to avoid actual API calls
        with patch('src.api.ask_endpoint.get_rag_agent_service') as mock_service:
            # Create a mock response
            mock_response = Mock()
            mock_response.answer = "This is a test answer"
            mock_response.sources = ["test_source_1", "test_source_2"]
            mock_response.matched_chunks = []
            mock_response.query_id = "test_query_id"

            # Configure the mock to return the mock response
            mock_service.return_value.process_query.return_value = mock_response

            # Make a request to the ask endpoint
            response = client.post(
                "/ask",
                json={"query": "What is retrieval augmented generation?"}
            )

            # Assert the response
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "sources" in data
            assert "matched_chunks" in data

    def test_ask_endpoint_empty_query(self):
        """Test that the ask endpoint returns an error for an empty query"""
        response = client.post(
            "/ask",
            json={"query": ""}
        )

        # Should return a 400 error for empty query
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error_code"] == "INVALID_QUERY"

    def test_ask_endpoint_missing_query(self):
        """Test that the ask endpoint returns an error for a missing query"""
        response = client.post(
            "/ask",
            json={}
        )

        # Should return a 422 error for missing query field
        assert response.status_code == 422

    def test_health_endpoint(self):
        """Test that the health endpoint returns a healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_ask_health_endpoint(self):
        """Test that the ask health endpoint returns a healthy status"""
        response = client.get("/ask/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data


def test_query_request_model():
    """Test the QueryRequest model validation"""
    # Valid query
    query_request = QueryRequest(query="What is RAG?")
    assert query_request.is_valid is True

    # Empty query
    query_request = QueryRequest(query="")
    assert query_request.is_valid is False

    # Long query
    long_query = "A" * 1001  # More than 1000 characters
    query_request = QueryRequest(query=long_query)
    assert query_request.is_valid is False


if __name__ == "__main__":
    pytest.main([__file__])