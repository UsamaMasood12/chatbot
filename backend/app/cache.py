"""
Response caching system for frequently asked questions
"""
import hashlib
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ResponseCache:
    """Cache responses to avoid redundant LLM calls"""
    
    def __init__(self, cache_file: str = "response_cache.json", ttl_hours: int = 24):
        """
        Initialize response cache
        
        Args:
            cache_file: Path to cache file
            ttl_hours: Time to live for cached responses in hours
        """
        self.cache_file = cache_file
        self.ttl_hours = ttl_hours
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache: {str(e)}")
        
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
    
    def _get_cache_key(self, query: str) -> str:
        """
        Generate cache key from query
        
        Args:
            query: User query
            
        Returns:
            Cache key (hash)
        """
        # Normalize query (lowercase, strip whitespace)
        normalized = query.lower().strip()
        # Create hash
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _is_expired(self, timestamp: str) -> bool:
        """
        Check if cached response is expired
        
        Args:
            timestamp: Cached timestamp
            
        Returns:
            True if expired
        """
        try:
            cached_time = datetime.fromisoformat(timestamp)
            expiry_time = cached_time + timedelta(hours=self.ttl_hours)
            return datetime.now() > expiry_time
        except Exception:
            return True
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response
        
        Args:
            query: User query
            
        Returns:
            Cached response or None
        """
        cache_key = self._get_cache_key(query)
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            
            # Check if expired
            if self._is_expired(cached_data.get('timestamp', '')):
                logger.info(f"Cache expired for query: {query[:50]}")
                del self.cache[cache_key]
                self._save_cache()
                return None
            
            logger.info(f"Cache hit for query: {query[:50]}")
            return cached_data.get('response')
        
        logger.info(f"Cache miss for query: {query[:50]}")
        return None
    
    def set(self, query: str, response: Dict[str, Any]):
        """
        Cache a response
        
        Args:
            query: User query
            response: Response to cache
        """
        cache_key = self._get_cache_key(query)
        
        self.cache[cache_key] = {
            'query': query[:100],  # Store truncated query for reference
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'hits': self.cache.get(cache_key, {}).get('hits', 0) + 1
        }
        
        self._save_cache()
        logger.info(f"Cached response for query: {query[:50]}")
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}
        self._save_cache()
        logger.info("Cache cleared")
    
    def clear_expired(self):
        """Remove expired entries from cache"""
        expired_keys = [
            key for key, data in self.cache.items()
            if self._is_expired(data.get('timestamp', ''))
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
            logger.info(f"Removed {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Cache stats
        """
        total_entries = len(self.cache)
        total_hits = sum(data.get('hits', 0) for data in self.cache.values())
        
        # Most cached queries
        top_queries = sorted(
            [
                {
                    'query': data.get('query', ''),
                    'hits': data.get('hits', 0),
                    'timestamp': data.get('timestamp', '')
                }
                for data in self.cache.values()
            ],
            key=lambda x: x['hits'],
            reverse=True
        )[:10]
        
        return {
            'total_entries': total_entries,
            'total_hits': total_hits,
            'ttl_hours': self.ttl_hours,
            'top_cached_queries': top_queries
        }


# Global cache instance
response_cache = ResponseCache(ttl_hours=24)