from fastapi import FastAPI
from dotenv import load_dotenv
import logging
from fastapi.middleware.cors import CORSMiddleware

from src.api.ask_endpoint import router as ask_router
from src.utils.config_validator import ConfigValidator
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Validate configurations at startup
config_validation = ConfigValidator.validate_all_configs()
if not config_validation["overall_valid"]:
    logger.error("Configuration validation failed. Some required configurations are missing.")
    raise RuntimeError("Configuration validation failed. Please check your environment variables.")

# Initialize the FastAPI app
app = FastAPI(
    title="RAG Agent API",
    description="API for the Retrieval-Augmented Generation Agent",
    version="1.0.0"
)

# Add CORS middleware to allow requests from the frontend
# For production, specify your GitHub Pages URL
frontend_url = os.getenv("FRONTEND_URL", "https://sadiaism.github.io")
additional_origins_str = os.getenv("ADDITIONAL_CORS_ORIGINS", "")
additional_origins = [origin.strip() for origin in additional_origins_str.split(",") if origin.strip()]

# Build the list of allowed origins
allowed_origins = [
    frontend_url,                    # Your GitHub Pages URL
    "http://localhost:3000",         # Local development (Docusaurus default)
    "http://localhost:8000",         # Local backend testing
    "http://127.0.0.1:3000",         # Alternative local development
    "http://127.0.0.1:8000",         # Alternative local backend
    "https://sadiaism.github.io",    # GitHub Pages (explicit)
    "https://*.github.io",           # GitHub Pages subdomains (if needed)
]

# Add any additional origins from environment variables
allowed_origins.extend(additional_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers that can be accessed by the frontend
    expose_headers=["Access-Control-Allow-Origin"]
)

# Include the ask endpoint router
app.include_router(ask_router, prefix="", tags=["ask"])

@app.get("/")
async def root():
    return {"message": "RAG Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)