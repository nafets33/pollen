import datetime
import os
import subprocess

from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from chess_piece.workerbees import queen_workerbees

# bee better

# Parameteres
WORFKLOW_DAG_ID = "run_workerbees"
WORFKFLOW_START_DATE = datetime.datetime(2023, 1, 1)
WORKFLOW_SCHEDULE_INTERVAL = "31 14 * * *"  # UTC >>> 9:30 EST 30 9
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
# Define jobs
start = EmptyOperator(task_id="start", dag=dag)
end = EmptyOperator(task_id="end", dag=dag)

qcp_s = ["castle", "bishop", "knight", "pawn1", "pawn_5"]

for val in qcp_s:
    dynamic_operator = PythonOperator(
        task_id=f"{val}-operator",
        python_callable=queen_workerbees,
        dag=dag,
        op_kwargs={"prod": True, "queens_chess_piece": "workerbee", "qcp_s": val},
    )
    start.set_downstream(dynamic_operator)
    dynamic_operator.set_downstream(end)

# start >> task_1_operator >> end
