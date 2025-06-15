import os
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
import aio_pika

from services.common import get_rabbitmq_connection, get_redis

app = FastAPI(title="API Server")
REQUEST_Q = os.getenv("REQUEST_Q", "airflow_requests")


class ProcessRequest(BaseModel):
    callback_url: str
    payload: dict = {}


@app.post("/process", status_code=202)
async def process(req: ProcessRequest):
    """Accept job request, stash callback in Redis, enqueue message."""
    correlation_id = str(uuid.uuid4())

    conn = await get_rabbitmq_connection()
    ch = await conn.channel()
    q = await ch.declare_queue(REQUEST_Q, durable=True)
    await ch.default_exchange.publish(
        aio_pika.Message(
            body=str(req.payload).encode(),
            correlation_id=correlation_id,
        ),
        routing_key=q.name,
    )

    redis = await get_redis()
    await redis.setex(correlation_id, 3600, req.callback_url)
    return {"correlation_id": correlation_id}
