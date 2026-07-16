"""Redis caching wrapper."""

import json
import redis
from typing import Optional, Any
from .config import REDIS_URL, CACHE_TTL_SECONDS


class Cache:
    """Redis cache client with in‑memory fallback."""

    def __init__(self, redis_url: str = REDIS_URL):
        """Initialize Redis connection. If Redis is unavailable, fall back to a simple dict cache."""
        self.available = False
        self.memory: dict[str, dict] = {}
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            self.client.ping()
            self.available = True
        except Exception as e:
            print(f"Warning: Redis unavailable: {e}")
            # Fallback to in‑memory cache (no TTL handling)
            self.client = None

    def get(self, key: str) -> Optional[dict]:
        """Retrieve cached value. Uses Redis when available, otherwise the in‑memory dict."""
        if self.available:
            try:
                value = self.client.get(key)
                return json.loads(value) if value else None
            except Exception as e:
                print(f"Cache get error (Redis): {e}")
                return None
        else:
            # In‑memory fallback
            return self.memory.get(key)

    def set(self, key: str, value: dict, ttl: int = CACHE_TTL_SECONDS) -> bool:
        """Cache value with TTL. Redis respects TTL; the in‑memory fallback ignores TTL."""
        if self.available:
            try:
                self.client.setex(key, ttl, json.dumps(value))
                return True
            except Exception as e:
                print(f"Cache set error (Redis): {e}")
                return False
        else:
            # Store in memory without TTL
            self.memory[key] = value
            return True

    def make_key(self, gene: str, hgvs: str) -> str:
        """Generate cache key."""
        return f"devscore:{gene}:{hgvs}".lower()


cache = Cache()
