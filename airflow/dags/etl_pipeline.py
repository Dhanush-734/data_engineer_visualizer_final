
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def hello_etl():

    print("ETL PIPELINE RUNNING")


with DAG(

    dag_id="etl_pipeline",

    start_date=datetime(2026, 1, 1),

    schedule="@daily",

    catchup=False

) as dag:

    etl_task = PythonOperator(

        task_id="run_etl",

        python_callable=hello_etl

    )

