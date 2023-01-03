from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
import datetime
import os
from airflow.models import DAG

import os


# Parameteres
WORFKLOW_DAG_ID = "run_workerbees"
WORFKFLOW_START_DATE = datetime.datetime(2022, 1, 1)
WORKFLOW_SCHEDULE_INTERVAL = "@once"
WORKFLOW_EMAIL = ["pollenq.queen@gmail.com"]

WORKFLOW_DEFAULT_ARGS = {
    "owner": "stefan stapinski",
    "start_date": WORFKFLOW_START_DATE,
    "email": WORKFLOW_EMAIL,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 0,
}
# Initialize DAG
dag = DAG(
    dag_id=WORFKLOW_DAG_ID,
    schedule=WORKFLOW_SCHEDULE_INTERVAL,
    default_args=WORKFLOW_DEFAULT_ARGS,
)
# Define functions
def job_1():
    print("Perform job 1")
    client_user = 'workerbees'
    cmd = f'screen -S {client_user}{"_"}{"workerbees"} python QueenWorkerBees.py -prod true'
    # screen -S bees python QueenWorkerBees.py -prod true
    os.system(cmd)

def job_2():
    print("Perform job 2")
    # cmd = f'screen -d {client_user}{"_"}{"workerbees"} python QueenWorkerBees.py'
    # os.system(cmd)

def sensor_job():
    print("Sensor Job")

# Define jobs
job_1_operator = PythonOperator(
    task_id="task_job_1",
    python_callable=job_1,
    dag=dag,
)

job_2_sensor = PythonSensor(
    task_id="task_job_2_sensor",
    python_callable=sensor_job,
    dag=dag,
    poke_interval=180,
)

job_2_operator = PythonOperator(
    task_id="task_job_2",
    python_callable=job_2,
    dag=dag,
)

job_1_operator >> job_2_sensor >> job_2_operator