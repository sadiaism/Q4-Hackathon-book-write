import requests
import json

# Test the backend API for CORS support
def test_backend():
    url = "http://localhost:8000/ask"

    # Test query
    test_data = {
        "query": "What is retrieval augmented generation?"
    }

    try:
        # Make a request to the backend
        response = requests.post(
            url,
            headers={
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:3000'  # Simulate a frontend origin
            },
            data=json.dumps(test_data)
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        # Check if CORS headers are present
        cors_headers = {k: v for k, v in response.headers.items() if 'cors' in k.lower() or 'allow' in k.lower()}
        print(f"CORS-related headers: {cors_headers}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to backend. Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_backend()