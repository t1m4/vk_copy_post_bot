import json
from typing import Dict

from aioredis import Redis


class AsyncRedisClient:
    DEFAULT_PREFIX = "user_"

    def __init__(self, redis_instance: Redis) -> None:
        self.redis = redis_instance

    async def set_mapping(self, user_id: str, value: Dict):
        """Set key with json value. Note: add DEFAULT_PREFIX to key."""
        str_value = json.dumps(value)
        key = "{}{}".format(self.DEFAULT_PREFIX, user_id)
        await self.redis.set(key, str_value)

    async def get_key(self, user_id: str) -> Dict:
        """Get key by key. Note: already have DEFAULT_PREFIX in user_id."""
        result = await self.redis.get(user_id)
        return json.loads(result)

    async def get_all_user_ids(self):
        result = await self.redis.keys("{}*".format(self.DEFAULT_PREFIX))
        return result
