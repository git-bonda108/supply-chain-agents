"""
Cache Manager for API Response Caching
"""

import os
import json
import sqlite3
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    SQLite-based cache manager for API responses.
    
    Provides:
    - Response caching with TTL
    - Automatic cache invalidation
    - Cache statistics
    """
    
    def __init__(self, db_path: str = "data/cache.db", ttl_seconds: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            db_path: Path to SQLite cache database
            ttl_seconds: Time-to-live for cache entries (default: 1 hour)
        """
        self.db_path = db_path
        self.ttl_seconds = int(os.getenv("CACHE_TTL_SECONDS", ttl_seconds))
        self.enabled = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        
        # Create cache directory if needed
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize cache database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
        """)
        
        conn.commit()
        conn.close()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Generate cache key from arguments.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            MD5 hash of serialized arguments
        """
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Dict]:
        """
        Get cached value.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/expired
        """
        if not self.enabled:
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT value, expires_at FROM cache
                WHERE key = ? AND expires_at > ?
            """, (key, datetime.now().isoformat()))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return json.loads(row[0])
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Dict, ttl_seconds: Optional[int] = None):
        """
        Set cached value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override
        """
        if not self.enabled:
            return
        
        try:
            ttl = ttl_seconds or self.ttl_seconds
            created_at = datetime.now()
            expires_at = created_at + timedelta(seconds=ttl)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO cache (key, value, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            """, (key, json.dumps(value), created_at.isoformat(), expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete cached value."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def clear_expired(self):
        """Clear expired cache entries."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cache WHERE expires_at <= ?", (datetime.now().isoformat(),))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM cache")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM cache WHERE expires_at > ?", (datetime.now().isoformat(),))
            active = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_entries": total,
                "active_entries": active,
                "expired_entries": total - active,
                "enabled": self.enabled
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"error": str(e)}


def cached(ttl_seconds: Optional[int] = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl_seconds: Optional TTL override
    """
    def decorator(func):
        cache = CacheManager()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache._generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


# Create singleton instance
def get_cache_manager() -> CacheManager:
    """Get cache manager instance."""
    return CacheManager()



