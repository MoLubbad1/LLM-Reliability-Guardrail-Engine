import hashlib
import json
import redis.asyncio as redis

class CacheService:
    def __init__(self):
        # Connects to local Redis server
        self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    def _generate_key(self, prompt: str) -> str:
        # Creates a secure hash for the prompt
        return hashlib.sha256(prompt.encode('utf-8')).hexdigest()

    async def get_cached_response(self, prompt: str):
        key = self._generate_key(prompt)
        data = await self.redis.get(key)
        if data:
            return json.loads(data) # Return the cached JSON
        return None

    async def set_cached_response(self, prompt: str, response_data: dict):
        key = self._generate_key(prompt)
        # Store in cache with an expiration of 1 hour
        await self.redis.setex(key, 3600, json.dumps(response_data))