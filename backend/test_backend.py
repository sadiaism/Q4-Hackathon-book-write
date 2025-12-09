import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qdrant_client import qdrant_manager
from rag import rag_service

load_dotenv()

async def test_backend():
    """
    Simple test to verify the backend components are working
    """
    print("Testing RAG Chatbot Backend...")

    # Test Qdrant connection
    print("\n1. Testing Qdrant connection...")
    try:
        info = qdrant_manager.get_collection_info()
        if info:
            print(f"✓ Qdrant connection successful. Collection info: {info}")
        else:
            print("✗ Qdrant connection failed")
    except Exception as e:
        print(f"✗ Qdrant connection failed: {e}")

    # Test LLM integration (using a simple query)
    print("\n2. Testing LLM integration...")
    try:
        # Test with a simple query that doesn't require context
        response = await rag_service.generate_response("Hello", [])
        print(f"✓ LLM integration working. Response preview: {response[:50]}...")
    except Exception as e:
        print(f"✗ LLM integration failed: {e}")

    # Test selected text response
    print("\n3. Testing selected text response...")
    try:
        sample_text = "The capital of France is Paris. Paris is located in Europe."
        response = await rag_service.generate_response_from_selected_text(
            "What is the capital of France?",
            sample_text
        )
        print(f"✓ Selected text response working. Response preview: {response[:50]}...")
    except Exception as e:
        print(f"✗ Selected text response failed: {e}")

    print("\n4. Testing sample RAG query...")
    try:
        response = await rag_service.process_rag_query("Hello, how are you?")
        print(f"✓ RAG query processing working. Response preview: {response.answer[:50]}...")
    except Exception as e:
        print(f"✗ RAG query processing failed: {e}")

    print("\nBackend test completed!")

if __name__ == "__main__":
    asyncio.run(test_backend())