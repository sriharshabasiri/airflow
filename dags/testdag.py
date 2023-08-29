from datetime import datetime
from airflow import DAG
from pendulum import datetime, duration
from airflow.operators.bash import BashOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": duration(minutes=1),
    "start_date" : datetime(2023, 1, 1),

    "conn_id": "postgres_default",

   # "host": "localhost",
   # "schema": "sriharshabasiri",
   # "login": "postgres",
   # "password": "postgres",
   # "port": 5432,
}

# Instantiate DAG
dag = DAG(
    dag_id='testdag',
    max_active_runs=3,
    schedule="@daily",
    default_args=default_args,
    catchup=False,
    # include path to look for external files
    template_searchpath="/Users/sriharshabasiri/airflow/include",
)

task1 = BashOperator(task_id='task1_stopserver', 
                     bash_command='echo "testing bashoperator for task1 - stopping server" >> /Users/sriharshabasiri/airflow/example1.txt',
                     dag=dag)

task2 = BashOperator(task_id='task2_copyscripts', 
                     bash_command='echo "testing bashoperator for task2 - copying scripts" >> /Users/sriharshabasiri/airflow/example2.txt',
                     dag=dag
                     )
task3 = SQLExecuteQueryOperator(
        task_id="task3_sql",
        sql='testsqlquery.sql',
        split_statements=True,
        return_last=False,
        dag=dag
    )

task4 = BashOperator(task_id='task4_startserver', 
                     bash_command='echo "testing bashoperator for task4 - starting server" >> /Users/sriharshabasiri/airflow/example4.txt',
                     dag=dag
                     )

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'github_to_staging',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Define the commands to execute in the BashOperator
checkout_code = """
    git clone https://github.com/your-username/your-repo.git /tmp/checkout_dir
"""

copy_to_staging = """
    rsync -av /tmp/checkout_dir/ staging_server:/path/to/staging/directory/
"""

# Define the tasks
checkout_task = BashOperator(
    task_id='checkout_code',
    bash_command=checkout_code,
    dag=dag,
)

copy_task = BashOperator(
    task_id='copy_to_staging',
    bash_command=copy_to_staging,
    dag=dag,
)

# Set task dependencies
checkout_task >> copy_task


task1 >> task2 >> task3 >> task4
