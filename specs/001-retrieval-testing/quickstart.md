# Quickstart: Retrieval & Pipeline Testing for RAG Ingestion

## Prerequisites

- Python 3.11 or higher
- Access to Qdrant instance with populated RAG collection
- Existing RAG pipeline data in Qdrant (from previous ingestion)
- Required packages from backend requirements

## Setup

1. **Install test dependencies:**
   ```bash
   pip install pytest python-dotenv
   ```

2. **Set up environment variables:**
   Ensure your `.env` file has the necessary Qdrant configuration:
   ```env
   QDRANT_URL=your_qdrant_url_here
   QDRANT_API_KEY=your_qdrant_api_key_here  # if applicable
   ```

3. **Verify Qdrant connection:**
   Make sure the Qdrant collection from the ingestion pipeline exists and has data.

## Usage

1. **Run basic retrieval tests:**
   ```bash
   python -m pytest backend/test_retrieval.py::test_basic_retrieval -v
   ```

2. **Run comprehensive validation:**
   ```bash
   python -m pytest backend/test_retrieval.py -v
   ```

3. **Run specific validation tests:**
   ```bash
   # Test content accuracy
   python -m pytest backend/test_retrieval.py::test_content_accuracy -v

   # Test metadata validation
   python -m pytest backend/test_retrieval.py::test_metadata_validation -v

   # Run end-to-end test
   python -m pytest backend/test_retrieval.py::test_end_to_end_retrieval -v
   ```

## Configuration

- **Collection name**: By default, tests will use the `rag_embedding` collection
- **Top-k value**: Default is 5, but can be configured per test
- **Timeout**: Default timeout for queries is 10 seconds
- **Test queries**: Predefined test queries are available in the test configuration

## Verification

After running the tests:
1. Check that retrieval accuracy meets the 95% threshold
2. Verify that all metadata fields (url, chunk_id) are correct
3. Confirm that JSON output follows the expected format
4. Review test execution time to ensure it meets the 2-second requirement