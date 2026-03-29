"""Error handling utilities for production"""

import time
import asyncio
from functools import wraps
from typing import Callable, Any

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator for handling transient failures"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (attempt + 1))
                        continue
            raise last_error
        return wrapper
    return decorator

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
    
    async def wait(self):
        """Wait if needed to respect rate limit"""
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_call = time.time()
