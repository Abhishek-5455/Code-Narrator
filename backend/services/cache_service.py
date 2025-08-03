import logging
from fastapi import HTTPException, Query
from fastapi.responses import PlainTextResponse
from cache_manager import file_cache

logger = logging.getLogger(__name__)

async def get_recent_files(limit: int = Query(10, ge=1, le=50)):
    """
    Get list of recently uploaded files from cache.
    
    Args:
        limit: Number of files to return (1-50, default: 10)
    """
    logger.info(f"Recent files requested - Limit: {limit}")
    recent_files = file_cache.get_recent_files(limit)
    logger.info(f"Retrieved {len(recent_files)} recent files from cache")
    
    return {
        "recent_files": recent_files,
        "total_returned": len(recent_files),
        "message": f"Retrieved {len(recent_files)} recent files"
    }

async def get_cached_file(file_id: str):
    """
    Get specific cached file content by file ID.
    
    Args:
        file_id: Unique identifier of the cached file
    """
    logger.info(f"Cached file requested - ID: {file_id}")
    cached_file = file_cache.get_file(file_id)
    
    if not cached_file:
        logger.warning(f"Cached file not found - ID: {file_id}")
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    logger.info(f"Cached file retrieved - ID: {file_id}, Filename: {cached_file.filename}, Language: {cached_file.language}")
    
    return {
        "file_id": file_id,
        "filename": cached_file.filename,
        "language": cached_file.language,
        "file_type": cached_file.file_type,
        "content": cached_file.content,
        "upload_time": cached_file.upload_time.isoformat(),
        "file_size": cached_file.file_size,
        "expires_at": cached_file.expires_at.isoformat()
    }

async def download_cached_file(file_id: str):
    """
    Download specific cached file as plain text.
    
    Args:
        file_id: Unique identifier of the cached file
    """
    logger.info(f"File download requested - ID: {file_id}")
    cached_file = file_cache.get_file(file_id)
    
    if not cached_file:
        logger.warning(f"Download failed - File not found: {file_id}")
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    logger.info(f"File download starting - ID: {file_id}, Filename: {cached_file.filename}")
    
    return PlainTextResponse(
        content=cached_file.content,
        headers={"Content-Disposition": f"attachment; filename={cached_file.filename}"}
    )

async def get_cache_stats():
    """Get comprehensive cache statistics."""
    logger.info("Cache statistics requested")
    stats = file_cache.get_cache_stats()
    logger.info(f"Cache stats - Total files: {stats['total_files']}, Total size: {stats['total_size_bytes']} bytes")
    
    return {
        "cache_stats": stats,
        "message": f"Cache contains {stats['total_files']} files"
    }

async def delete_cached_file(file_id: str):
    """
    Delete a specific cached file.
    
    Args:
        file_id: Unique identifier of the cached file
    """
    logger.info(f"Delete cached file requested - ID: {file_id}")
    success = file_cache.delete_file(file_id)
    
    if not success:
        logger.warning(f"Failed to delete cached file - ID not found: {file_id}")
        raise HTTPException(status_code=404, detail="File not found")
    
    logger.info(f"Cached file deleted successfully - ID: {file_id}")
    
    return {
        "file_id": file_id,
        "message": "File deleted successfully"
    }

async def clear_all_cache():
    """Clear all cached files."""
    logger.info("Clear all cache requested")
    deleted_count = file_cache.clear_cache()
    logger.info(f"Cache cleared - {deleted_count} files deleted")
    
    return {
        "deleted_files": deleted_count,
        "message": f"Cleared {deleted_count} files from cache"
    }

async def search_cached_files(
    language: str = Query(None, description="Filter by programming language"),
    file_type: str = Query(None, description="Filter by file type (uploaded/generated)"),
    filename: str = Query(None, description="Filter by filename (partial match)")
):
    """
    Search cached files with optional filters.
    
    Args:
        language: Filter by programming language (Python, Java, JavaScript)
        file_type: Filter by file type (uploaded, generated)
        filename: Filter by filename (partial match)
    """
    logger.info(f"File search requested - Language: {language}, Type: {file_type}, Filename: {filename}")
    
    all_files = file_cache.get_recent_files(limit=100)  # Get more files for filtering
    logger.info(f"Retrieved {len(all_files)} files for filtering")
    
    filtered_files = all_files
    
    if language:
        filtered_files = [f for f in filtered_files if f['language'].lower() == language.lower()]
        logger.info(f"Filtered by language '{language}': {len(filtered_files)} files")
    
    if file_type:
        filtered_files = [f for f in filtered_files if f['file_type'].lower() == file_type.lower()]
        logger.info(f"Filtered by type '{file_type}': {len(filtered_files)} files")
    
    if filename:
        filtered_files = [f for f in filtered_files if filename.lower() in f['filename'].lower()]
        logger.info(f"Filtered by filename '{filename}': {len(filtered_files)} files")
    
    logger.info(f"Search completed - Found {len(filtered_files)} matching files")
    
    return {
        "files": filtered_files,
        "total_found": len(filtered_files),
        "filters_applied": {
            "language": language,
            "file_type": file_type,
            "filename": filename
        }
    } 