# RAG Pipeline: Embedding & Retrieval Testing

This project includes two main components:
1. **Embedding Pipeline**: Extracts text from Docusaurus URLs, generates embeddings using Cohere, and stores them in Qdrant
2. **Retrieval Testing Framework**: Validates that stored vectors in Qdrant can be retrieved accurately

## Prerequisites

- Python 3.11 or higher
- UV package manager
- Cohere API key
- Qdrant instance (cloud or self-hosted)

## Setup

1. **Install UV package manager** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   uv pip install -r requirements.txt
   # For testing framework:
   pip install -r requirements-test.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the backend directory with your API keys:
   ```env
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_URL=your_qdrant_url_here  # Leave empty for local Qdrant
   QDRANT_API_KEY=your_qdrant_api_key_here  # If using Qdrant Cloud
   ```

## Usage

### Embedding Pipeline
Run the complete ingestion pipeline:
```bash
cd backend
python main.py
```

The pipeline will:
1. Crawl the target Docusaurus site (https://sadiaism.github.io/Q4-Hackathon-book-write/)
2. Extract text content from all discovered pages
3. Chunk the text appropriately
4. Generate embeddings using Cohere
5. Store embeddings in Qdrant collection named `rag_embedding`

### Retrieval Testing Framework
Run the retrieval validation tests:
```bash
cd backend
python test_retrieval.py
```

Or run specific tests with pytest:
```bash
python -m pytest test_retrieval.py::run_sample_tests -v
```

The testing framework will:
1. Connect to the existing Qdrant collection (`rag_embedding`)
2. Generate embeddings for sample queries using Cohere
3. Query Qdrant with top-k search
4. Validate retrieved chunks against original text
5. Verify metadata (url, chunk_id) correctness
6. Return clean JSON output for end-to-end test results

## Configuration

### Embedding Pipeline
- **Target URL**: Modify in the `main()` function to crawl different Docusaurus sites
- **Max Pages**: Adjust `max_pages` parameter in `get_all_urls()` to control crawl depth
- **Chunk Size**: Adjust `chunk_size` and `overlap` parameters in `chunk_text()` function
- **Cohere Model**: Currently using `embed-multilingual-v3.0` model

### Retrieval Testing Framework
- **Collection Name**: By default, tests will use the `rag_embedding` collection
- **Top-k value**: Default is 5, configurable via `DEFAULT_TOP_K` in test_config.py
- **Timeout**: Default timeout for queries is 10 seconds
- **Test queries**: Predefined test queries are available in the test configuration

## Architecture

### Embedding Pipeline
- `get_all_urls()`: Crawls and discovers all URLs from a base Docusaurus site
- `extract_text_from_url()`: Extracts clean text content from a single URL
- `chunk_text()`: Splits text into overlapping chunks to preserve context
- `embed()`: Generates vector embeddings using Cohere API
- `create_collection()`: Creates Qdrant collection named `rag_embedding`
- `save_chunks_to_qdrant()`: Stores embeddings with metadata in Qdrant
- `main()`: Orchestrates the entire pipeline execution

### Retrieval Testing Framework
- `connect_to_qdrant()`: Access existing Qdrant collection
- `generate_query_embedding()`: Generate embedding for sample queries using Cohere
- `query_qdrant_with_topk()`: Perform top-k search in Qdrant
- `validate_retrieved_chunks()`: Compare retrieved chunks against original text
- `verify_metadata_correctness()`: Validate metadata (url, chunk_id) retrieval
- `end_to_end_retrieval_test()`: Complete pipeline test with clean JSON output

## Troubleshooting

- If you get rate limit errors from Cohere, consider adding more delays between API calls
- For large sites, you may need to adjust the `max_pages` parameter to avoid excessive crawling
- Make sure your Qdrant instance is running if using a local installation
- Verify that the `rag_embedding` collection exists before running retrieval tests

## Hugging Face Space Configuration

If you want to deploy this as a Hugging Face Space using Docker, use the following Space configuration:

title: "RAG Agent API"
emoji: ðŸ¤—
colorFrom: blue
colorTo: red
sdk: docker
pinned: false
license: mit
---

### Environment Variables for Space Secrets

- `GEMINI_API_KEY`: Your Google Gemini API key
- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_URL`: Your Qdrant database URL
- `QDRANT_API_KEY`: Your Qdrant API key
- `FRONTEND_URL`: Your frontend URL

### API Endpoints

- `/` - Root endpoint
- `/health` - Health check endpoint
- `/ask` - Main endpoint for asking questions to the RAG agent