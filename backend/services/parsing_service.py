import os
import time
import logging
from fastapi import UploadFile, File
from parser.python_parser import parse_code_to_markdown as parse_python_to_markdown
from parser.java_parser import parse_code_to_markdown as parse_java_to_markdown
from parser.javascript_parser import parse_code_to_markdown as parse_javascript_to_markdown
from cache_manager import file_cache

logger = logging.getLogger(__name__)

async def parse_code_endpoint(file: UploadFile = File(...)):
    """
    Upload a code file and generate markdown documentation.
    Supports Python (.py), Java (.java), and JavaScript (.js/.jsx) files.
    Returns the generated markdown content and file information.
    """
    start_time = time.time()
    
    logger.info(f"Parse code endpoint accessed - File: {file.filename}, Size: {file.size} bytes")
    
    # Check file type before processing
    filename = file.filename.lower()
    supported_extensions = ['.py', '.java', '.js', '.jsx']
    
    if not any(filename.endswith(ext) for ext in supported_extensions):
        logger.warning(f"Unsupported file type uploaded: {file.filename}")
        return {
            "error": "Unsupported file type",
            "filename": file.filename,
            "supported_types": [".py (Python)", ".java (Java)", ".js/.jsx (JavaScript)"],
            "message": "Please upload a Python, Java, or JavaScript file"
        }
    
    # Determine language
    if filename.endswith('.py'):
        language = "Python"
    elif filename.endswith('.java'):
        language = "Java"
    elif filename.endswith('.js') or filename.endswith('.jsx'):
        language = "JavaScript"
    
    logger.info(f"Processing {language} file: {file.filename}")
    
    try:
        # Read file content
        content = await file.read()
        code_content = content.decode('utf-8')
        
        logger.info(f"File content read successfully - Characters: {len(code_content)}")
        
        # Store uploaded file in cache
        try:
            uploaded_file_id = file_cache.store_file(file.filename, code_content, 'uploaded')
            logger.info(f"File stored in cache with ID: {uploaded_file_id}")
        except Exception as e:
            logger.error(f"Failed to store file in cache: {e}")
            # Continue without cache storage
            uploaded_file_id = "cache_error"
        
        try:
            # Generate markdown documentation directly
            logger.info(f"Detected {language} file, using {language} parser")
            
            if filename.endswith('.py'):
                markdown_content = parse_python_to_markdown(code_content)
            elif filename.endswith('.java'):
                markdown_content = parse_java_to_markdown(code_content)
            elif filename.endswith('.js') or filename.endswith('.jsx'):
                markdown_content = parse_javascript_to_markdown(code_content)
            
            # Store generated markdown in cache
            markdown_filename = f"{os.path.splitext(file.filename)[0]}_docs.md"
            generated_file_id = file_cache.store_file(markdown_filename, markdown_content, 'generated')
            
            processing_time = time.time() - start_time
            logger.info(f"Documentation generated successfully - Generated file ID: {generated_file_id}, Processing time: {processing_time:.2f}s")
            
            return {
                "filename": file.filename,
                "language": language,
                "uploaded_file_id": uploaded_file_id,
                "generated_file_id": generated_file_id,
                "markdown_content": markdown_content,
                "message": f"Successfully generated {language} documentation"
            }
        except ValueError as e:
            processing_time = time.time() - start_time
            logger.error(f"Processing error for file {file.filename}: {str(e)}, Time: {processing_time:.2f}s")
            return {
                "error": "Processing error",
                "filename": file.filename,
                "message": str(e)
            }
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Unexpected error processing file {file.filename}: {str(e)}, Time: {processing_time:.2f}s")
            return {
                "error": "Unexpected error",
                "filename": file.filename,
                "message": f"Failed to process file: {str(e)}"
            }
                
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Critical error in parse endpoint for file {file.filename}: {str(e)}, Time: {processing_time:.2f}s")
        return {
            "error": "Critical error",
            "filename": file.filename,
            "message": f"System error: {str(e)}"
        } 