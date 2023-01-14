from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
from airflow.api.client.local_client import Client
import datetime
import os, time
# import subprocess
from airflow.models import DAG
import os
import pickle
import pytz
import pandas as pd

est = pytz.timezone("US/Eastern")
# from King hive_master_root

airflow_dag__main_root = os.getcwd() # hive_master_root() 
j=os.path.join(airflow_dag__main_root, 'pollen')
client_dbs = os.path.join(j, 'client_user_dbs')

# dag_queen_PKL = os.path.join(airflow_dag__main_root, 'queen_dagger.pkl')
# if os.path.exists(dag_queen_PKL) == False:
#     print("init dag queen")
#     PickleData(dag_queen_PKL, {'reqeuest_read': pd.DataFrame()})






# def PickleData(pickle_file, data_to_store):

#     p_timestamp = {'pq_last_modified': datetime.datetime.now(est)}
#     root, name = os.path.split(pickle_file)
#     pickle_file_temp = os.path.join(root, ("temp" + name))
#     with open(pickle_file_temp, 'wb+') as dbfile:
#         db = data_to_store
#         db['pq_last_modified'] = p_timestamp
#         pickle.dump(db, dbfile)
    
#     with open(pickle_file, 'wb+') as dbfile:
#         db = data_to_store
#         db['pq_last_modified'] = p_timestamp
#         pickle.dump(db, dbfile)
     
#     return True


# def ReadPickleData(pickle_file): 

#     # Check the file's size and modification time
#     prev_size = os.stat(pickle_file).st_size
#     prev_mtime = os.stat(pickle_file).st_mtime
#     while True:
#         stop = 0
#         # Get the current size and modification time of the file
#         curr_size = os.stat(pickle_file).st_size
#         curr_mtime = os.stat(pickle_file).st_mtime
        
#         # Check if the size or modification time has changed
#         if curr_size != prev_size or curr_mtime != prev_mtime:
#             print(f'{pickle_file} is currently being written to')
#             # logging.info(f'{pickle_file} is currently being written to')
#         else:
#             if stop > 3:
#                 print("pickle error")
#                 # logging.critical(f'{e} error is pickle load')
#                 # send_email(subject='CRITICAL Read Pickle Break')
#                 break
#             try:
#                 with open(pickle_file, "rb") as f:
#                     return pickle.load(f)
#             except Exception as e:
#                 print(e)
#                 # logging.error(f'{e} error is pickle load')
#                 stop+=1
#                 time.sleep(0.033)

#         # Update the previous size and modification time
#         prev_size = curr_size
#         prev_mtime = curr_mtime
        
#         # Wait a short amount of time before checking again
#         time.sleep(0.033)










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

print(vars(dag))

# Define functions

def job_runqueen(**kwargs):
    # read QueenDagger and check to see if there are any new queens to spin up
    parameter = kwargs['dag_run'].conf["client_user"]
    print(parameter)
    
    prod = kwargs['dag_run'].conf["prod"]
    client_user = kwargs['dag_run'].conf["client_user"]
    
    client_user_name = f'queen__{prod}_{client_user}' #stefanstapinski
    cmd = f'screen -S {client_user_name} python QueenBee.Py -prod true -client_user {client_user_name}'
    os.system(cmd)
    # subprocess.run(["screen", "-S", f'{client_user}', "&&", "python", "QueenBee.Py"])

    cmd = f'screen -d {client_user_name}'
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