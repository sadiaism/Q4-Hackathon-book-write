from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class QueryRequest(BaseModel):
    """
    Model for the query request from the user
    """
    query: str = Field(..., description="The natural language question from the user")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context or parameters for the query")

    class Config:
        schema_extra = {
            "example": {
                "query": "What is retrieval-augmented generation?",
                "metadata": {}
            }
        }

    @property
    def is_valid(self) -> bool:
        """Check if the query is valid (not empty and within reasonable length)"""
        return bool(self.query and 0 < len(self.query) < 1000)


class QueryVector(BaseModel):
    """
    Model for the vector representation of a query
    """
    vector: List[float] = Field(..., description="Numerical representation of the query")
    query_text: str = Field(..., description="Original query text for reference")

    class Config:
        schema_extra = {
            "example": {
                "vector": [0.1, 0.2, 0.3, 0.4],
                "query_text": "What is retrieval-augmented generation?"
            }
        }


class RetrievedChunk(BaseModel):
    """
    Model for a chunk retrieved from the knowledge base
    """
    content: str = Field(..., description="Text content retrieved from knowledge base")
    source: str = Field(..., description="Source identifier for the content")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score to the query")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional information about the chunk")

    class Config:
        schema_extra = {
            "example": {
                "content": "RAG combines retrieval and generation models to improve accuracy...",
                "source": "source1.pdf",
                "score": 0.85,
                "metadata": {}
            }
        }


class ResponseObject(BaseModel):
    """
    Model for the response object returned to the user
    """
    answer: str = Field(..., description="The generated answer to the user's query")
    sources: List[str] = Field(..., description="List of sources used to generate the answer")
    matched_chunks: List[RetrievedChunk] = Field(..., description="The text chunks used to generate the answer")
    query_id: Optional[str] = Field(None, description="Identifier for tracking the query")

    class Config:
        schema_extra = {
            "example": {
                "answer": "Retrieval-augmented generation (RAG) is a technique that combines...",
                "sources": ["source1.pdf", "source2.docx"],
                "matched_chunks": [
                    {
                        "content": "RAG combines retrieval and generation models to improve accuracy...",
                        "source": "source1.pdf",
                        "score": 0.85
                    }
                ],
                "query_id": "query-12345"
            }
        }


class ErrorObject(BaseModel):
    """
    Model for error responses
    """
    error_code: str = Field(..., description="Code identifying the type of error")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

    class Config:
        schema_extra = {
            "example": {
                "error_code": "INVALID_QUERY",
                "message": "Query cannot be empty",
                "details": {}
            }
        }