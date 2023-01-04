from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
import datetime
import os
# import subprocess
from airflow.models import DAG
import os



# Parameteres
WORFKLOW_DAG_ID = "run_queenbee_prod"
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
def job_runqueen():
    # print("Perform job 1")
    client_user = 'queen_stefanstapinski'
    cmd = f'screen -S {client_user} python QueenBee.Py -prod true -bee_scheduler true'
    os.system(cmd)
    # subprocess.run(["screen", "-S", f'{client_user}', "&&", "python", "QueenBee.Py"])


def job_2():
    print("Perform job 2")

def sensor_job():
    print("Sensor Job")

# Define jobs
job_1_operator = PythonOperator(
    task_id="task_job_1",
    python_callable=job_runqueen,
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