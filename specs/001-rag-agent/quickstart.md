# Quickstart: RAG Agent with FastAPI and Retrieval Integration

## Prerequisites

- Python 3.11
- pip package manager
- Access to OpenAI API
- Access to Cohere API
- Qdrant vector database instance

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install fastapi openai cohere qdrant-client uvicorn
   ```

4. **Set up environment variables:**
   Create a `.env` file with the following:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   COHERE_API_KEY=your_cohere_api_key
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key
   ```

## Running the Service

1. **Start the FastAPI server:**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

2. **The service will be available at:**
   - API Documentation: `http://localhost:8000/docs`
   - Query endpoint: `http://localhost:8000/ask`

## Making a Query

**Example request:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is retrieval-augmented generation?"
  }'
```

**Expected response:**
```json
{
  "answer": "Retrieval-augmented generation (RAG) is a technique that...",
  "sources": ["source1.pdf", "source2.docx"],
  "matched_chunks": [
    {
      "content": "RAG combines retrieval and generation...",
      "source": "source1.pdf"
    }
  ]
}
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Configuration

The service can be configured through environment variables:
- `QDRANT_URL`: URL for the Qdrant vector database
- `QDRANT_API_KEY`: API key for Qdrant access
- `COHERE_API_KEY`: API key for Cohere embeddings
- `OPENAI_API_KEY`: API key for OpenAI services
- `MODEL_NAME`: The model to use for generation (default: gpt-3.5-turbo)