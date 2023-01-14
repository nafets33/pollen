from airflow.api.client.local_client import Client
import subprocess
import datetime
import pytz
est = pytz.timezone("US/Eastern")
import streamlit as st





def run__trigger_dag(dag_id, run_id, client_user, prod):
    # dag_id='run_queenbee_prod'
    c = Client(None, None)
    c.trigger_dag(dag_id=dag_id, run_id=run_id, conf={'client_user': client_user, 'prod': prod})
    # st.info(client_user)


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

# # Example usage
# processes = get_screen_processes()
# print(processes)

### for everymorning check to see if workerbees is running, if its not turn the dag on
def workerbees___the_beeManager(client_user='QueenBeeDagger'):
    avail_dags = {'run_queenbee_prod': 'run_queenbee_prod', 'run_workerbees': 'run_workerbees'}
    
    processes = get_screen_processes()
    run_id = f'{datetime.datetime.now(est)}___run_workerbees'
    if 'run_workerbees' not in processes.keys():
        run__trigger_dag(dag_id='run_workerbees', run_id=run_id, client_user='QueenBeeDagger')


