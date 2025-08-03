import time
import hashlib
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


# Configure logging for cache manager
logger = logging.getLogger(__name__)

@dataclass
class CachedFile:
    """Represents a cached file with metadata"""
    filename: str
    content: str
    language: str
    file_type: str  # 'uploaded' or 'generated'
    upload_time: datetime
    file_size: int
    file_hash: str
    expires_at: datetime

class FileCache:
    """In-memory cache for uploaded and generated files"""
    
    def __init__(self, max_files: int = 100, expiration_hours: int = 24):
        self.cache: Dict[str, CachedFile] = {}
        self.max_files = max_files
        self.expiration_hours = expiration_hours
    
    def _generate_file_id(self, filename: str, content: str) -> str:
        """Generate unique ID for file based on filename and content hash"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = int(time.time())
        return f"{filename}_{content_hash}_{timestamp}"
    
    def _cleanup_expired(self):
        """Remove expired files from cache"""
        now = datetime.now()
        expired_keys = [
            key for key, cached_file in self.cache.items()
            if cached_file.expires_at < now
        ]
        if expired_keys:
            logger.info(f"Cleaning up {len(expired_keys)} expired files from cache")
        for key in expired_keys:
            del self.cache[key]
    
    def _enforce_size_limit(self):
        """Remove oldest files if cache exceeds max_files limit"""
        if len(self.cache) <= self.max_files:
            return
        
        files_to_remove = len(self.cache) - self.max_files
        logger.info(f"Cache size limit exceeded ({len(self.cache)}/{self.max_files}), removing {files_to_remove} oldest files")
        
        # Sort by upload time and remove oldest
        sorted_items = sorted(
            self.cache.items(),
            key=lambda x: x[1].upload_time
        )
        
        # Remove oldest files until we're under the limit
        for i in range(files_to_remove):
            key = sorted_items[i][0]
            filename = sorted_items[i][1].filename
            logger.debug(f"Removing oldest file from cache: {filename} (ID: {key})")
            del self.cache[key]
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        filename_lower = filename.lower()
        if filename_lower.endswith('.py'):
            return 'Python'
        elif filename_lower.endswith('.java'):
            return 'Java'
        elif filename_lower.endswith(('.js', '.jsx')):
            return 'JavaScript'
        else:
            return 'Unknown'
    
    def store_file(self, filename: str, content: str, file_type: str = 'uploaded') -> str:
        """
        Store file in cache and return unique file ID
        
        Args:
            filename: Original filename
            content: File content
            file_type: 'uploaded' or 'generated'
        
        Returns:
            Unique file ID for retrieval
        """
        logger.info(f"Storing file in cache - Filename: {filename}, Type: {file_type}, Size: {len(content)} chars")
        
        self._cleanup_expired()
        
        file_id = self._generate_file_id(filename, content)
        language = self._detect_language(filename)
        
        cached_file = CachedFile(
            filename=filename,
            content=content,
            language=language,
            file_type=file_type,
            upload_time=datetime.now(),
            file_size=len(content),
            file_hash=hashlib.md5(content.encode()).hexdigest(),
            expires_at=datetime.now() + timedelta(hours=self.expiration_hours)
        )
        
        self.cache[file_id] = cached_file
        self._enforce_size_limit()
        
        logger.info(f"File stored successfully - ID: {file_id}, Language: {language}, Expires: {cached_file.expires_at}")
        
        return file_id
    
    def get_file(self, file_id: str) -> Optional[CachedFile]:
        """Retrieve file from cache by ID"""
        logger.debug(f"Retrieving file from cache - ID: {file_id}")
        self._cleanup_expired()
        
        cached_file = self.cache.get(file_id)
        if cached_file:
            logger.info(f"File retrieved successfully - ID: {file_id}, Filename: {cached_file.filename}")
        else:
            logger.warning(f"File not found in cache - ID: {file_id}")
        
        return cached_file
    
    def get_recent_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of recent files with metadata (without content)"""
        self._cleanup_expired()
        
        # Sort by upload time (newest first)
        sorted_files = sorted(
            self.cache.items(),
            key=lambda x: x[1].upload_time,
            reverse=True
        )
        
        recent_files = []
        for file_id, cached_file in sorted_files[:limit]:
            recent_files.append({
                'file_id': file_id,
                'filename': cached_file.filename,
                'language': cached_file.language,
                'file_type': cached_file.file_type,
                'upload_time': cached_file.upload_time.isoformat(),
                'file_size': cached_file.file_size,
                'expires_at': cached_file.expires_at.isoformat()
            })
        
        return recent_files
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file from cache"""
        logger.info(f"Deleting file from cache - ID: {file_id}")
        
        if file_id in self.cache:
            filename = self.cache[file_id].filename
            del self.cache[file_id]
            logger.info(f"File deleted successfully - ID: {file_id}, Filename: {filename}")
            return True
        
        logger.warning(f"File not found for deletion - ID: {file_id}")
        return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        logger.debug("Generating cache statistics")
        self._cleanup_expired()
        
        languages = {}
        file_types = {}
        total_size = 0
        
        for cached_file in self.cache.values():
            # Count by language
            languages[cached_file.language] = languages.get(cached_file.language, 0) + 1
            
            # Count by file type
            file_types[cached_file.file_type] = file_types.get(cached_file.file_type, 0) + 1
            
            # Sum total size
            total_size += cached_file.file_size
        
        stats = {
            'total_files': len(self.cache),
            'max_files': self.max_files,
            'total_size_bytes': total_size,
            'expiration_hours': self.expiration_hours,
            'languages': languages,
            'file_types': file_types
        }
        
        logger.info(f"Cache stats generated - Files: {stats['total_files']}, Size: {total_size} bytes, Languages: {list(languages.keys())}")
        
        return stats
    
    def clear_cache(self) -> int:
        """Clear all files from cache and return count of deleted files"""
        count = len(self.cache)
        logger.info(f"Clearing cache - {count} files will be deleted")
        
        self.cache.clear()
        
        logger.info(f"Cache cleared successfully - {count} files deleted")
        return count

# Global cache instance
file_cache = FileCache(max_files=100, expiration_hours=24)
logger.info(f"File cache initialized - Max files: {file_cache.max_files}, Expiration: {file_cache.expiration_hours}h") 