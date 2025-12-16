# Quickstart: Embedding Pipeline Setup

## Prerequisites

- Python 3.11 or higher
- UV package manager
- Cohere API key
- Qdrant instance (cloud or self-hosted)

## Setup

1. **Create backend directory and install dependencies:**
   ```bash
   mkdir backend
   cd backend
   uv init
   uv pip install cohere qdrant-client requests beautifulsoup4 python-dotenv
   ```

2. **Set up environment variables:**
   Create a `.env` file in the backend directory:
   ```env
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_URL=your_qdrant_url_here
   QDRANT_API_KEY=your_qdrant_api_key_here  # if using cloud
   ```

3. **Prepare the main.py file:**
   Create `main.py` with the complete implementation containing all required functions.

## Usage

1. **Run the pipeline:**
   ```bash
   cd backend
   python main.py
   ```

2. **The pipeline will:**
   - Crawl the provided Docusaurus URL (https://sadiaism.github.io/Q4-Hackathon-book-write/)
   - Extract text content from all pages
   - Chunk the text appropriately
   - Generate embeddings using Cohere
   - Store embeddings in Qdrant collection named `rag_embedding`

## Configuration

- **Target URL**: Modify in the main function to crawl different Docusaurus sites
- **Chunk size**: Adjust in the chunk_text function (default: 1000 characters)
- **Overlap**: Adjust in the chunk_text function (default: 200 characters)
- **Cohere model**: Modify in the embed function (default: embed-multilingual-v3.0)

## Verification

After running the pipeline:
1. Check Qdrant dashboard to confirm embeddings are stored
2. Verify the `rag_embedding` collection contains the expected number of vectors
3. Test similarity search to ensure embeddings are functional