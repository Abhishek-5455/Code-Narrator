import time
import logging
from fastapi import UploadFile, File
from suggestor.python_suggestor import suggest_refactor
from suggestor.java_suggestor import suggest_refactor_java
from suggestor.javascript_suggestor import suggest_refactor_javascript
from cache_manager import file_cache

logger = logging.getLogger(__name__)

async def suggest_refactoring(file: UploadFile = File(...)):
    """
    Upload a code file and get language-specific refactoring suggestions.
    Supports Python (.py), Java (.java), and JavaScript (.js) files.
    """
    start_time = time.time()
    logger.info(f"Suggest endpoint accessed - File: {file.filename}, Size: {file.size} bytes")
    
    try:
        content = await file.read()
        code_content = content.decode()
        
        logger.info(f"File content read for suggestions - Characters: {len(code_content)}")
        
        # Store uploaded file in cache
        try:
            uploaded_file_id = file_cache.store_file(file.filename, code_content, 'uploaded')
            logger.info(f"File stored in cache with ID: {uploaded_file_id}")
        except Exception as e:
            logger.error(f"Failed to store file in cache: {e}")
            uploaded_file_id = "cache_error"
        
        # Detect language based on file extension
        filename = file.filename.lower()
        
        if filename.endswith('.py'):
            logger.info("Generating Python refactoring suggestions")
            suggestions = suggest_refactor(code_content)
            language = "Python"
        elif filename.endswith('.java'):
            logger.info("Generating Java refactoring suggestions")
            suggestions = suggest_refactor_java(code_content)
            language = "Java"
        elif filename.endswith('.js') or filename.endswith('.jsx'):
            logger.info("Generating JavaScript refactoring suggestions")
            suggestions = suggest_refactor_javascript(code_content)
            language = "JavaScript"
        else:
            logger.warning(f"Unsupported file type for suggestions: {file.filename}")
            return {
                "error": "Unsupported file type",
                "supported_types": [".py (Python)", ".java (Java)", ".js/.jsx (JavaScript)"],
                "filename": file.filename
            }
        
        processing_time = time.time() - start_time
        logger.info(f"Suggestions generated successfully - Language: {language}, Count: {len(suggestions)}, Time: {processing_time:.2f}s")
        
        return {
            "filename": file.filename,
            "language": language,
            "uploaded_file_id": uploaded_file_id,
            "total_suggestions": len(suggestions),
            "suggestions": suggestions
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error generating suggestions for file {file.filename}: {str(e)}, Time: {processing_time:.2f}s")
        return {
            "error": "Processing error",
            "filename": file.filename,
            "message": f"Failed to generate suggestions: {str(e)}"
        } 