from fastapi import FastAPI
from dotenv import load_dotenv
import logging
from fastapi.middleware.cors import CORSMiddleware

from src.api.ask_endpoint import router as ask_router
from src.utils.config_validator import ConfigValidator

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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