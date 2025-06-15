import os
import aio_pika
import aioredis


async def get_rabbitmq_connection():
    """Return a robust RabbitMQ connection (async)."""
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")
    return await aio_pika.connect_robust(url)


async def get_redis():
    """Return an async Redis client."""
    url = os.getenv("REDIS_URL", "redis://redis-master:6379/0")
    return await aioredis.from_url(url, decode_responses=True)
