import json
from typing import List, Dict, Optional

import aioredis

from app_logging import logger


class RedisClient:
    """
    Class for interacting with Redis asynchronously.
    """

    def __init__(self, redis_url: str):
        """
        Initializes the RedisClient with the specified Redis URL.

        :param redis_url: The Redis URL for connection (e.g., "redis://localhost:6379").
        """
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        """
        Asynchronously connects to the Redis server.
        """
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis at {self.redis_url}: {e}")
            raise

    async def close(self):
        """
        Asynchronously closes the connection to the Redis server.
        """
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

    async def get_value(self, key: str) -> Optional[str]:
        """
        Asynchronously gets the value associated with the provided key from Redis.

        :param key: The key for which to retrieve the value.
        :return: The value associated with the key if it exists, None otherwise.
        """
        try:
            if not self.redis:
                await self.connect()

            value = await self.redis.get(key)
            if value is not None:
                logger.info(f"Retrieved value for key '{key}': {value.decode('utf-8')}")
                return value.decode('utf-8')
            else:
                logger.info(f"No value found for key '{key}'")
                return None
        except Exception as e:
            logger.error(f"Error retrieving value for key '{key}': {e}")
            return None
