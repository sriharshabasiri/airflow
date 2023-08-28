from datetime import datetime
import os
from airflow import DAG
from pendulum import datetime, duration
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": "['harshabasiri@gmail.com']", 
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 1,
    "retry_delay": duration(minutes=1),
    "start_date" : datetime(2023, 1, 1),

    "conn_id": "email",

   # "host": "localhost",
   # "schema": "sriharshabasiri",
   # "login": "postgres",
   # "password": "postgres",
   # "port": 5432,
}

# Instantiate DAG
dag = DAG(
    dag_id='dynamicdag2',
    max_active_runs=3,
    schedule="@daily",
    default_args=default_args,
    catchup=False,
    # include path to look for external files
    template_searchpath="/Users/sriharshabasiri/airflow/include",
)

scriptfile = " /Users/sriharshabasiri/airflow/finaclescript2.sh "
#if os.path.exists(scriptfile):
task0 = BashOperator(task_id= 'task0_finaclescript2',
        bash_command=scriptfile,
        dag=dag
   )

task1= EmailOperator(
       task_id='task1_sendmail_userconf',
       to='harshabasiri@gmail.com',
       subject='Alert Mail',
       html_content=""" Mail Test """,
       dag=dag
)

task0 >> task1