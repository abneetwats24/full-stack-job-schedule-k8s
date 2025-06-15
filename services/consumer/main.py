import asyncio
import os
import aio_pika
from airflow_client.client import ApiClient, Configuration, DagRunApi

from services.common import get_rabbitmq_connection

REQUEST_Q = os.getenv("REQUEST_Q", "airflow_requests")
DAG_ID = os.getenv("DAG_ID", "sleep_dag")
AIRFLOW_HOST = os.getenv("AIRFLOW_HOST", "http://airflow-webserver:8080")


async def trigger_dag(correlation_id: str, payload: str):
    cfg = Configuration(host=AIRFLOW_HOST, username="admin", password="admin")
    async with ApiClient(cfg) as api:
        dr_api = DagRunApi(api)
        await dr_api.post_dag_run(
            dag_id=DAG_ID,
            dag_run={'conf': {'correlation_id': correlation_id, 'payload': payload}},
        )


async def main():
    conn = await get_rabbitmq_connection()
    ch = await conn.channel()
    q = await ch.declare_queue(REQUEST_Q, durable=True)

    async with q.iterator() as iterator:
        async for msg in iterator:
            async with msg.process():
                await trigger_dag(msg.correlation_id, msg.body.decode())


if __name__ == "__main__":
    asyncio.run(main())
