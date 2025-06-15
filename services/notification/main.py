import asyncio
import os
import aio_pika
import httpx

from services.common import get_rabbitmq_connection, get_redis

RESULT_Q = os.getenv("RESULT_Q", "airflow_results")


async def handle(message: aio_pika.IncomingMessage):
    async with message.process():
        corr = message.correlation_id
        redis = await get_redis()
        callback = await redis.get(corr)
        if callback:
            async with httpx.AsyncClient() as client:
                await client.post(callback, json={"result": message.body.decode(), "correlation_id": corr})


async def main():
    conn = await get_rabbitmq_connection()
    ch = await conn.channel()
    q = await ch.declare_queue(RESULT_Q, durable=True)
    async with q.iterator() as iterator:
        async for msg in iterator:
            await handle(msg)


if __name__ == "__main__":
    asyncio.run(main())
