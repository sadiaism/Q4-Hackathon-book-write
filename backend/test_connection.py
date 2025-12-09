import asyncio
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qdrant_client_fixed import qdrant_manager

load_dotenv()

async def test_connection():
    """
    Test the backend connection components
    """
    print("Testing RAG Chatbot Backend Connections...")
    print("=" * 50)

    # Test Qdrant connection
    print("\n1. Testing Qdrant connection...")
    try:
        info = qdrant_manager.get_collection_info()
        if info:
            print(f"✓ Qdrant connection successful!")
            print(f"  - Collection: {info.get('name', 'N/A')}")
            print(f"  - Vector size: {info.get('vector_size', 'N/A')}")
            print(f"  - Points count: {info.get('points_count', 'N/A')}")
            print(f"  - Status: {info.get('status', 'active')}")
        else:
            print("✗ Qdrant connection failed")
    except Exception as e:
        print(f"✗ Qdrant connection failed: {e}")

    # Test environment variables
    print("\n2. Testing environment variables...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    print(f"✓ GEMINI_API_KEY: {'Set' if gemini_key and len(gemini_key) > 10 else 'Not set or too short'}")

    # Test a simple search
    print("\n3. Testing search functionality...")
    try:
        results = qdrant_manager.search_similar_texts("test query", limit=2)
        print(f"✓ Search functionality working, found {len(results)} results")
        if results:
            print(f"  - First result preview: {results[0]['text'][:50]}...")
    except Exception as e:
        print(f"✗ Search functionality failed: {e}")

    print("\n" + "=" * 50)
    print("Connection test completed!")

if __name__ == "__main__":
    asyncio.run(test_connection())