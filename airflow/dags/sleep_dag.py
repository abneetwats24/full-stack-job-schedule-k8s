"""Minimal DAG: sleeps 1–2 s then publishes result to RabbitMQ."""

from datetime import datetime
import os, random, time, pika
from airflow import DAG
from airflow.operators.python import PythonOperator

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")
RESULT_Q = os.getenv("RESULT_Q", "airflow_results")

def task_fn(**ctx):
    corr = ctx['dag_run'].conf.get('correlation_id')
    dur = random.randint(1, 2)
    time.sleep(dur)
    publish(corr, f"slept {dur}s")

def publish(corr_id, msg):
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    ch = conn.channel()
    ch.queue_declare(queue=RESULT_Q, durable=True)
    ch.basic_publish('', RESULT_Q, msg.encode(), properties=pika.BasicProperties(correlation_id=corr_id))
    conn.close()

default_args = {"start_date": datetime(2025, 1, 1), "owner": "airflow"}
with DAG('sleep_dag', schedule_interval=None, catchup=False, default_args=default_args) as dag:
    PythonOperator(task_id='sleep_and_publish', python_callable=task_fn)
