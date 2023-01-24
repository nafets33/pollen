import datetime
import os
import subprocess

from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from chess_piece.queen_bee import queenbee


# Parameteres
WORFKLOW_DAG_ID = "run_queenbee"
WORFKFLOW_START_DATE = datetime.datetime(2023, 1, 1)
WORKFLOW_SCHEDULE_INTERVAL = None
WORKFLOW_EMAIL = ["pollenq.queen@gmail.com"]

WORKFLOW_DEFAULT_ARGS = {
    "owner": "stefan stapinski",
    "start_date": WORFKFLOW_START_DATE,
    "email": WORKFLOW_EMAIL,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
}

def job_runqueen(**kwargs):

    # read QueenDagger and check to see if there are any new queens to spin up
    parameter = kwargs['dag_run'].conf["client_user"]
    print(parameter)

    client_user = kwargs['dag_run'].conf["client_user"]
    prod = kwargs['dag_run'].conf["prod"]
    prod_strname = 'true' if prod else 'false'
    queenbee(client_user=client_user, prod=prod_strname, queens_chess_piece='queen')

    return True

# Initialize DAG
dag = DAG(
    dag_id=WORFKLOW_DAG_ID,
    schedule=WORKFLOW_SCHEDULE_INTERVAL,
    default_args=WORKFLOW_DEFAULT_ARGS,
    catchup=False,
)
# Define jobs
start = EmptyOperator(task_id="start", dag=dag)

task_1_operator = PythonOperator(
    task_id="queenbee_task_job_1",
    python_callable=job_runqueen,
    dag=dag,
    # op_kwargs={"prod": "", "queens_chess_piece": "workerbee"},
)

end = EmptyOperator(task_id="end", dag=dag)

start >> task_1_operator >> end
