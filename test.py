import asyncio

from app.api.redis_client import RedisClient
from app.loader import redis_client
from app.models.OpenAi import summarize_context


async def test():
    history = await redis_client.get_user_history(user_id='2069609909')
    if len(history) > 1:
        summary = await summarize_context(history)
        new_history = [{'role': 'assistant', 'content': summary}]
        await redis_client.update_user_history(user_id='2069609909', new_history=new_history)
    history = await redis_client.get_user_history(user_id='2069609909')
    print(history)
    return None

asyncio.run(test())