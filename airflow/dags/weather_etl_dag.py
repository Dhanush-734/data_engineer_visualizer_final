from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests


def trigger_etl():
    requests.get("http://web:5000/run-etl")


with DAG(
    dag_id="weather_etl_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
) as dag:

    run_etl_task = PythonOperator(
        task_id="run_weather_etl",
        python_callable=trigger_etl,
    )