import datetime
import os
import subprocess

from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from chess_piece.queen_worker_bees import queen_workerbees


def get_screen_processes():
    # Run the "screen -ls" command to get a list of screen processes
    output = subprocess.run(["screen", "-ls"], stdout=subprocess.PIPE).stdout.decode(
        "utf-8"
    )

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
WORFKLOW_DAG_ID = "run_workerbees"
WORFKFLOW_START_DATE = datetime.datetime(2023, 1, 1)
WORKFLOW_SCHEDULE_INTERVAL = "30 9 * * *"
WORKFLOW_EMAIL = ["pollenq.queen@gmail.com"]

WORKFLOW_DEFAULT_ARGS = {
    "owner": "stefan stapinski",
    "start_date": WORFKFLOW_START_DATE,
    "email": WORKFLOW_EMAIL,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
}
# Initialize DAG
dag = DAG(
    dag_id=WORFKLOW_DAG_ID,
    schedule=WORKFLOW_SCHEDULE_INTERVAL,
    default_args=WORKFLOW_DEFAULT_ARGS,
    catchup=False,
)
# Define functions
def job_1():

    bees = "workerbees"
    processes_ = get_screen_processes()
    if bees not in processes_:
        print("Perform job 1")
        cmd = f"screen -S {bees} python QueenWorkerBees.py -prod true"
        os.system(cmd)

        cmd = f"screen -d {bees}"
        os.system(cmd)


# Define jobs
start = EmptyOperator(task_id="start", dag=dag)

task_1_operator = PythonOperator(
    task_id="task_job_1",
    python_callable=queen_workerbees,
    dag=dag,
    op_kwargs={"prod": "", "queens_chess_piece": "workerbee"},
)

end = EmptyOperator(task_id="end", dag=dag)

start >> task_1_operator >> end
