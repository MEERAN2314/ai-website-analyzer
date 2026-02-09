import redis.asyncio as aioredis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        """Connect to Redis"""
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        return self.redis
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str):
        """Get value from Redis"""
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = None):
        """Set value in Redis"""
        await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        """Delete key from Redis"""
        await self.redis.delete(key)
    
    async def incr(self, key: str):
        """Increment value"""
        return await self.redis.incr(key)
    
    async def expire(self, key: str, seconds: int):
        """Set expiration"""
        await self.redis.expire(key, seconds)

redis_client = RedisClient()
