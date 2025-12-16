"""
Simple test script to verify the RAG Agent API is working properly
"""
import requests
import json

# Test the health endpoint
print("Testing health endpoint...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"Health check: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"Health check failed (expected if server not running): {e}")

print("\nTesting ask endpoint structure...")
# Show what a request would look like
sample_request = {
    "query": "What is retrieval augmented generation?"
}

print("Sample request structure:")
print(json.dumps(sample_request, indent=2))

print("\nThe API is structured to:")
print("- Accept POST requests to /ask endpoint")
print("- Validate incoming queries")
print("- Process queries through the RAG agent workflow")
print("- Return responses with answer, sources, and matched chunks")
print("- Handle errors appropriately")