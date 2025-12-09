from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
import os
import uuid
from dotenv import load_dotenv
import asyncio
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_db, create_tables
from models import Chat, ChatMessage
from auth import get_current_active_user, User
from rag import rag_service, RAGQuery, SelectedTextQuery, RAGResponse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Create tables on startup
create_tables()

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="A Retrieval-Augmented Generation chatbot API using Qdrant, Gemini, and PostgreSQL",
    version="1.0.0"
)

# Add CORS middleware
origins = os.getenv("BACKEND_CORS_ORIGINS", ["http://localhost:3000", "http://localhost:3001", "https://your-frontend-domain.com"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The user's message/question")
    user_id: str = Field(..., min_length=1, max_length=100, description="The ID of the user")
    chat_id: Optional[str] = Field(None, min_length=1, max_length=100, description="The ID of the chat session")
    book_id: Optional[str] = Field(None, min_length=1, max_length=100, description="The ID of the book to search in")

    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError('User ID cannot be empty')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict]
    chat_id: str

class SelectedTextChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The user's message/question")
    selected_text: str = Field(..., min_length=1, max_length=5000, description="The text selected by the user")
    user_id: str = Field(..., min_length=1, max_length=100, description="The ID of the user")
    chat_id: Optional[str] = Field(None, min_length=1, max_length=100, description="The ID of the chat session")

    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

    @validator('selected_text')
    def validate_selected_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Selected text cannot be empty')
        return v.strip()

    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError('User ID cannot be empty')
        return v.strip()

class IngestRequest(BaseModel):
    text_chunks: List[Dict] = Field(..., min_items=1, description="List of text chunks to ingest")
    book_id: str = Field(..., min_length=1, max_length=100, description="The ID of the book/document")

    @validator('book_id')
    def validate_book_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Book ID cannot be empty')
        return v.strip()

    @validator('text_chunks')
    def validate_text_chunks(cls, v):
        if not v:
            raise ValueError('Text chunks cannot be empty')
        if len(v) > 1000:  # Reasonable limit
            raise ValueError('Too many text chunks (max 1000)')
        for chunk in v:
            if 'text' not in chunk or not chunk['text'] or not chunk['text'].strip():
                raise ValueError('Each chunk must have non-empty text')
        return v

class IngestResponse(BaseModel):
    success: bool
    message: str
    chunks_processed: int

@app.on_event("startup")
async def startup_event():
    """
    Startup event to initialize the application
    """
    print("Starting up RAG Chatbot API...")
    # You can add any initialization logic here

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event to clean up resources
    """
    print("Shutting down RAG Chatbot API...")

@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running
    """
    return {"message": "RAG Chatbot API is running!"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "RAG Chatbot API"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
    """
    Ingest document chunks into the vector database
    """
    try:
        logger.info(f"Processing ingestion request for book: {request.book_id}, {len(request.text_chunks)} chunks")

        # Validate the request
        if not request.text_chunks:
            raise HTTPException(status_code=400, detail="No text chunks provided for ingestion")

        if not request.book_id:
            raise HTTPException(status_code=400, detail="Book ID is required for ingestion")

        #success = qdrant_manager.add_text_chunks(request.text_chunks, request.book_id)
        #if success:
            logger.info(f"Successfully ingested {len(request.text_chunks)} chunks for book: {request.book_id}")
            return IngestResponse(
                success=True,
                message=f"Successfully ingested {len(request.text_chunks)} chunks",
                chunks_processed=len(request.text_chunks)
            )
        else:
            logger.error(f"Failed to ingest document chunks for book: {request.book_id}")
            raise HTTPException(status_code=500, detail="Failed to ingest document chunks")
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, current_user: User = Depends(get_current_active_user)):
    """
    Chat endpoint for general RAG answers from the full knowledge base
    """
    try:
        logger.info(f"Processing chat request for user: {request.user_id}, book_id: {request.book_id}")

        # Generate a chat ID if not provided
        chat_id = request.chat_id or str(uuid.uuid4())

        # Validate that the message is not too short
        if len(request.message.strip()) < 3:
            raise HTTPException(status_code=400, detail="Message is too short, minimum 3 characters required")

        # Process the RAG query
        rag_response = await rag_service.process_rag_query(request.message, request.book_id)

        # In a real implementation, you would save the chat messages to the database
        # For now, we're just returning the response

        logger.info(f"Successfully processed chat request for user: {request.user_id}")
        return ChatResponse(
            response=rag_response.answer,
            sources=rag_response.sources,
            chat_id=chat_id
        )
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.post("/chat-selected", response_model=ChatResponse)
async def chat_selected_endpoint(request: SelectedTextChatRequest, current_user: User = Depends(get_current_active_user)):
    """
    Chat endpoint that ONLY answers from user-selected text
    """
    try:
        logger.info(f"Processing selected text chat request for user: {request.user_id}")

        # Generate a chat ID if not provided
        chat_id = request.chat_id or str(uuid.uuid4())

        # Validate that the message is not too short
        if len(request.message.strip()) < 3:
            raise HTTPException(status_code=400, detail="Message is too short, minimum 3 characters required")

        # Validate that selected text is not too short
        if len(request.selected_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Selected text is too short, minimum 10 characters required")

        # Process the query against selected text only
        rag_response = await rag_service.process_selected_text_query(
            request.message,
            request.selected_text
        )

        logger.info(f"Successfully processed selected text chat request for user: {request.user_id}")
        return ChatResponse(
            response=rag_response.answer,
            sources=rag_response.sources,
            chat_id=chat_id
        )
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error processing selected text chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing selected text chat request: {str(e)}")

@app.get("/qdrant-info")
async def get_qdrant_info():
    """
    Get information about the Qdrant collection
    """
    # try:
        # info = qdrant_manager.get_collection_info()
        # return info
    # except Exception as e:
        # raise HTTPException(status_code=500, detail=f"Error getting Qdrant info: {str(e)}")

@app.post("/reset-knowledge-base")
async def reset_knowledge_base():
    """
    Reset the entire knowledge base (use with caution!)
    """
    try:
        # This would delete the entire Qdrant collection
        success = qdrant_manager.delete_collection()
        if success:
            # Recreate the collection
            qdrant_manager._create_collection()
            return {"message": "Knowledge base reset successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset knowledge base")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting knowledge base: {str(e)}")

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.exception_handler(404)
async def not_found_handler(request, exc):
    logger.warning(f"404 error: {str(request.url)}")
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"500 error: {str(exc)} at {str(request.url)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "path": str(request.url), "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)} at {str(request.url)}")
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred", "path": str(request.url), "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)