from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from services.parsing_service import parse_code_endpoint
from services.suggestion_service import suggest_refactoring
from services.cache_service import (
    get_recent_files, get_cached_file, download_cached_file, 
    get_cache_stats, delete_cached_file, clear_all_cache, search_cached_files
)
from cache_manager import file_cache

# Configure logging
log_file_path = os.path.join(os.getcwd(), 'codenarrator.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ],
    force=True  # Force reconfiguration if already configured
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://127.0.0.1:3000",  # Alternative localhost format
        "http://localhost:3001",  # Alternative React port
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Initialize logging and cache
logger.info("CodeNarrator API starting up...")
logger.info("Logging system initialized successfully")
logger.info("CORS middleware configured for frontend communication")

# Test cache initialization
try:
    cache_stats = file_cache.get_cache_stats()
    logger.info(f"Cache system initialized - {cache_stats}")
except Exception as e:
    logger.error(f"Cache initialization failed: {e}")



@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "CodeNarrator API is running!",
        "endpoints": {
            "POST /parse-code/": "Upload code files (.py, .java, .js/.jsx) to generate markdown documentation",
            "POST /suggest/": "Upload code files (.py, .java, .js/.jsx) to get language-specific refactoring suggestions",
            "GET /files/recent": "Get list of recently uploaded files",
            "GET /files/{file_id}": "Get specific cached file content",
            "GET /files/{file_id}/download": "Download cached file as plain text",
            "GET /files/stats": "Get cache statistics",
            "GET /files/search": "Search cached files with filters",
            "DELETE /files/{file_id}": "Delete specific cached file",
            "DELETE /files/clear": "Clear all cached files",
            "GET /docs": "Interactive API documentation"
        },
        "supported_languages": {
            "Python": ".py files",
            "Java": ".java files", 
            "JavaScript": ".js, .jsx files"
        },
        "note": "File upload endpoints require POST requests. Use /docs to test them interactively."
    }



# @app.post("/parse-content/")
# async def parse_content(file: UploadFile = File(...)):
#     content = await file.read()
#     markdown = parse_code_to_markdown(content.decode())
#     return {"markdown": markdown}

@app.post("/parse-code/")
async def parse_code_route(file: UploadFile = File(...)):
    """
    Upload a code file and generate markdown documentation.
    Supports Python (.py), Java (.java), and JavaScript (.js/.jsx) files.
    Returns the generated markdown content and file information.
    """
    return await parse_code_endpoint(file)

@app.post("/suggest/")
async def suggest_route(file: UploadFile = File(...)):
    """
    Upload a code file and get language-specific refactoring suggestions.
    Supports Python (.py), Java (.java), and JavaScript (.js) files.
    """
    return await suggest_refactoring(file)

# Cache Management APIs

@app.get("/files/recent")
async def get_recent_files_route(limit: int = Query(10, ge=1, le=50)):
    """Get list of recently uploaded files from cache."""
    return await get_recent_files(limit)

@app.get("/files/{file_id}")
async def get_cached_file_route(file_id: str):
    """Get specific cached file content by file ID."""
    return await get_cached_file(file_id)

@app.get("/files/{file_id}/download", response_class=PlainTextResponse)
async def download_cached_file_route(file_id: str):
    """Download specific cached file as plain text."""
    return await download_cached_file(file_id)

@app.get("/files/stats")
async def get_cache_stats_route():
    """Get comprehensive cache statistics."""
    return await get_cache_stats()

@app.delete("/files/{file_id}")
async def delete_cached_file_route(file_id: str):
    """Delete a specific cached file."""
    return await delete_cached_file(file_id)

@app.delete("/files/clear")
async def clear_all_cache_route():
    """Clear all cached files."""
    return await clear_all_cache()

@app.get("/files/search")
async def search_cached_files_route(
    language: str = Query(None, description="Filter by programming language"),
    file_type: str = Query(None, description="Filter by file type (uploaded/generated)"),
    filename: str = Query(None, description="Filter by filename (partial match)")
):
    """Search cached files with optional filters."""
    return await search_cached_files(language, file_type, filename)
