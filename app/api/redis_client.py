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

    async def set_value(self, key: str, value: str, expire: Optional[int] = None):
        """
        Set a value in Redis with an optional expiration time in one operation.

        :param key: Redis key
        :param value: Value to store
        :param expire: Optional expiration time in seconds.
        """
        try:
            if not self.redis:
                await self.connect()

            if expire:
                await self.redis.set(key, value, ex=expire)
            else:
                await self.redis.set(key, value)
        except Exception as e:
            logger.error(f"Error setting value for key '{key}': {e}")

    async def delete_value(self, key: str) -> bool:
        """
        Deletes the history of a user by removing the associated key from Redis.

        :param user_id: The ID of the user whose history should be deleted.
        """
        try:
            if not self.redis:
                await self.connect()

            result = await self.redis.delete(key)

            if result:
                return True
            else:
                return False

        except Exception as e:
            return False

    async def set_user_history(self, user_id: str, history: List[Dict], expire: Optional[int] = None):
        """
        Stores a user's history (list of dictionaries) in Redis.

        :param user_id: Unique identifier for the user.
        :param history: List of dictionaries representing user history.
        :param expire: Optional expiration time in seconds.
        """
        try:
            if not self.redis:
                await self.connect()

            key = f"history:{user_id}"
            value = json.dumps(history)

            await self.redis.set(key, value, ex=expire)
            logger.info(f"Set history for user '{user_id}' in Redis.")
        except Exception as e:
            logger.error(f"Error setting history for user '{user_id}': {e}")

    async def get_user_history(self, user_id: str) -> Optional[List[Dict]]:
        """
        Retrieves a user's history from Redis.

        :param user_id: Unique identifier for the user.
        :return: List of dictionaries representing the user's history, or None if not found.
        """
        try:
            if not self.redis:
                await self.connect()

            key = f"history:{user_id}"
            value = await self.redis.get(key)

            if value is not None:
                history = json.loads(value.decode('utf-8'))
                logger.info(f"Retrieved history for user '{user_id}' from Redis.")
                return history
            else:
                logger.info(f"No history found for user '{user_id}'.")
                return None
        except Exception as e:
            logger.error(f"Error retrieving history for user '{user_id}': {e}")
            return None

    async def append_to_user_history(self, user_id: str, new_message: str, user: bool = True):
        """
        Appends a new message to the user's history stored in Redis.

        :param user_id: Unique identifier for the user.
        :param new_message: Dictionary representing the latest user or bot message.
        """
        try:
            if not self.redis:
                await self.connect()

            current_history = await self.get_user_history(user_id) or []
            if user:
                role = 'user'
            else:
                role = 'assistant'
            if current_history is None:
                await self.set_user_history(user_id=user_id, history=[{"role": role, "content": new_message}])

            current_history.append({"role": role, "content": new_message})

            await self.set_user_history(user_id, current_history)
            logger.info(f"Appended new message to history for user '{user_id}'.")
        except Exception as e:
            logger.error(f"Error appending to history for user '{user_id}': {e}")

    async def delete_user_history(self, user_id: str):
        """
        Deletes the history of a user by removing the associated key from Redis.

        :param user_id: The ID of the user whose history should be deleted.
        """
        try:
            if not self.redis:
                await self.connect()

            key = f"history:{user_id}"
            result = await self.redis.delete(key)

            if result:
                logger.info(f"Successfully deleted history for user '{user_id}'.")
                return True
            else:
                logger.info(f"No history found for user '{user_id}' to delete.")
                return False

        except Exception as e:
            logger.error(f"Error deleting history for user '{user_id}': {e}")
            return False

    async def update_user_history(self, user_id: int, new_history: List[Dict[str, str]]):
        history_json = json.dumps(new_history)
        await self.redis.set(f'history:{user_id}', history_json)
