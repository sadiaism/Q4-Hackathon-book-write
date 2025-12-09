# RAG Chatbot Backend

A complete production-ready Retrieval-Augmented Generation (RAG) chatbot backend built with FastAPI, OpenAI, Gemini, Qdrant, and PostgreSQL.

## Features

- **RAG Chatbot**: Answers questions based on your Docusaurus documentation
- **Two Query Modes**:
  - General RAG: Answers from the full knowledge base
  - Selected Text: Answers only from user-selected text
- **Vector Storage**: Uses Qdrant Cloud for efficient similarity search
- **Database**: Neon Serverless PostgreSQL for user and chat history
- **Authentication**: Token-based authentication ready
- **Async Support**: Fully async FastAPI backend
- **Error Handling**: Comprehensive error handling and validation

## Prerequisites

- Python 3.8+
- Qdrant Cloud account (free tier available)
- OpenAI API key (for primary model)
- Google Gemini API key (for fallback model)
- Neon PostgreSQL account (for production)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd your-repo-name/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Edit the `.env` file with your API keys and database URLs:
```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database
NEON_DATABASE_URL=your_neon_database_url_here

# Qdrant
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=book_embeddings

# Authentication
SECRET_KEY=your_secret_key_here
```

## Running the Backend

1. Start the development server:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. The API will be available at `http://localhost:8000`

3. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

### Ingestion
- `POST /ingest` - Ingest document chunks into the vector database

### Chat
- `POST /chat` - General RAG chat (answers from full knowledge base)
- `POST /chat-selected` - Selected text chat (answers only from user-selected text)

### Utility
- `GET /health` - Health check
- `GET /qdrant-info` - Get Qdrant collection information
- `POST /reset-knowledge-base` - Reset the entire knowledge base (use with caution!)

## Ingesting Your Documentation

To ingest your Docusaurus documentation:

1. Use the `/ingest` endpoint with your text chunks, or
2. Use the `ingest_pipeline.py` script:

```python
from ingest_pipeline import DocumentIngestor
import asyncio

async def main():
    ingestor = DocumentIngestor()

    # Ingest from Docusaurus docs directory
    await ingestor.ingest_from_docusaurus_docs("./path/to/your/docs", "my_docusaurus_book")

if __name__ == "__main__":
    asyncio.run(main())
```

## Frontend Integration

To connect your Docusaurus frontend to this backend:

1. Set the backend URL in your frontend:
```javascript
const BACKEND_URL = 'http://localhost:8000'; // or your production URL
```

2. Make requests to the chat endpoints:
```javascript
// General RAG chat
fetch(`${BACKEND_URL}/chat`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-jwt-token'
  },
  body: JSON.stringify({
    message: 'Your question here',
    user_id: 'user-123',
    book_id: 'optional-book-id'
  })
})

// Selected text chat
fetch(`${BACKEND_URL}/chat-selected`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-jwt-token'
  },
  body: JSON.stringify({
    message: 'Your question here',
    selected_text: 'The text the user selected',
    user_id: 'user-123'
  })
})
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (primary model)
- `GEMINI_API_KEY`: Your Google Gemini API key (fallback model)
- `NEON_DATABASE_URL`: Your Neon PostgreSQL connection string
- `QDRANT_URL`: Your Qdrant Cloud URL
- `QDRANT_API_KEY`: Your Qdrant API key
- `QDRANT_COLLECTION_NAME`: Name of the Qdrant collection (default: book_embeddings)
- `SECRET_KEY`: Secret key for JWT token generation
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

### CORS Configuration

Update the `BACKEND_CORS_ORIGINS` in your environment to include your frontend domains:

```python
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://your-frontend-domain.com"]
```

## Architecture

- **FastAPI**: Web framework with automatic API documentation
- **OpenAI**: Primary LLM for response generation
- **Google Gemini**: Fallback LLM when OpenAI fails
- **Qdrant**: Vector database for semantic search
- **PostgreSQL**: Relational database for user and chat data
- **Sentence Transformers**: For generating text embeddings
- **JWT**: Token-based authentication

## Production Deployment

For production deployment:

1. Use a production WSGI/ASGI server like Gunicorn:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. Set up proper SSL certificates
3. Configure a reverse proxy (nginx, Apache)
4. Set up proper logging and monitoring
5. Use environment-specific configuration

## Error Handling

The API includes comprehensive error handling:
- Validation errors return 422 status codes
- Authentication errors return 401 status codes
- Authorization errors return 403 status codes
- Not found errors return 404 status codes
- Server errors return 500 status codes with detailed messages

## Security

- JWT-based authentication
- Input validation on all endpoints
- Rate limiting (implement as needed)
- SQL injection prevention through SQLAlchemy
- XSS prevention through proper response encoding

## Testing

To run the application:

1. Start the backend: `uvicorn main:app --reload`
2. Navigate to `http://localhost:8000/docs` to test the API endpoints
3. Use the interactive API documentation to test functionality