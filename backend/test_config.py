"""
Configuration for retrieval testing framework
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = "rag_embedding"  # Default collection name

# Cohere configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Test configuration
DEFAULT_TOP_K = 5
QUERY_TIMEOUT = 10  # seconds