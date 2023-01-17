from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
from airflow.api.client.local_client import Client
import datetime
import os, time
# import subprocess
from airflow.models import DAG
import subprocess

def get_screen_processes():
    # Run the "screen -ls" command to get a list of screen processes
    output = subprocess.run(["screen", "-ls"], stdout=subprocess.PIPE).stdout.decode("utf-8")

    # Split the output into lines
    lines = output.strip().split("\n")

    # The first line is a header, so skip it
    lines = lines[1:]

    # Initialize an empty dictionary
    screen_processes = {}

    # Iterate over the lines and extract the process name and PID
    for line in lines:
        parts = line.split()
        name = parts[0]
        pid = parts[1]
        screen_processes[name] = pid

    return screen_processes


# Parameteres
WORFKLOW_DAG_ID = "run_queenbee_prod"
WORFKFLOW_START_DATE = datetime.datetime(2022, 1, 1)
WORKFLOW_SCHEDULE_INTERVAL = None # "* * * * *"
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

print(vars(dag))

# Define functions

def job_runqueen(**kwargs):

    existing_processes = get_screen_processes()

    # read QueenDagger and check to see if there are any new queens to spin up
    parameter = kwargs['dag_run'].conf["client_user"]
    print(parameter)
    
    prod = kwargs['dag_run'].conf["prod"]
    client_user = kwargs['dag_run'].conf["client_user"]
    
    prod_strname = 'true' if prod else 'false'
    client_process_name = f'queen__{prod_strname}_{client_user}' #stefanstapinski

    cmd = f'screen -S {client_process_name} python QueenBee.Py -prod {prod_strname} -client_user {client_user}'
    os.system(cmd)
    # subprocess.run(["screen", "-S", f'{client_user}', "&&", "python", "QueenBee.Py"])

    cmd = f'screen -d {client_process_name}'
    os.system(cmd)


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