from fastapi import APIRouter, HTTPException, status
from typing import Optional
import logging

from ..models.query import QueryRequest, ResponseObject, ErrorObject
from ..services.rag_agent import RAGAgentService
from .utils import APIResponseUtils

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Initialize the RAG agent service
rag_agent_service: Optional[RAGAgentService] = None


def get_rag_agent_service() -> RAGAgentService:
    """
    Get or create the RAG agent service instance
    """
    global rag_agent_service
    if rag_agent_service is None:
        try:
            rag_agent_service = RAGAgentService()
        except Exception as e:
            logger.error(f"Failed to initialize RAG agent service: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize RAG agent service"
            )
    return rag_agent_service


@router.post("/ask", response_model=ResponseObject)
async def ask_endpoint(query_request: QueryRequest):
    """
    Endpoint to handle user queries and return answers with sources and matched chunks.

    Args:
        query_request: The query request containing the user's question

    Returns:
        ResponseObject containing the answer, sources, and matched chunks
    """
    logger.info(f"Received query: {query_request.query}")

    try:
        # Validate the query request
        if not query_request.is_valid:
            error_obj = ErrorObject(
                error_code="INVALID_QUERY",
                message="Query cannot be empty and must be less than 1000 characters",
                details={"query_length": len(query_request.query) if query_request.query else 0}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_obj.dict()
            )

        # Get the RAG agent service
        rag_service = get_rag_agent_service()

        # Process the query through the RAG agent
        response = rag_service.process_query(query_request)

        logger.info("Query processed successfully")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ask endpoint: {e}")

        error_obj = ErrorObject(
            error_code="INTERNAL_ERROR",
            message="An internal error occurred while processing the query",
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_obj.dict()
        )


@router.get("/ask/health")
async def ask_endpoint_health():
    """
    Health check for the ask endpoint
    """
    try:
        rag_service = get_rag_agent_service()
        return {"status": "healthy", "message": "Ask endpoint is ready to process queries"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ask endpoint is not ready"
        )