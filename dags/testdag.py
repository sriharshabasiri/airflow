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
    'backup_modified_and_rsync',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Define the paths for backup and staging directories
backup_root_dir = "/tmp/backup_dir/{{ ds_nodash }}"
staging_dir = "/path/to/staging/directory"
checkout_dir = "/tmp/checkout_dir"

# Define the rsync command with the --backup and --backup-dir options
rsync_files = """
    rsync -av --backup --backup-dir={backup_root_dir}/{staging_relative_path} {checkout_dir}/{staging_relative_path}/ {staging_dir}/{staging_relative_path}/
""".format(
    backup_root_dir=backup_root_dir,
    checkout_dir=checkout_dir,
    staging_dir=staging_dir,
    staging_relative_path="{{ item }}",
)

# Define the backup task for each subdirectory in the staging directory
backup_task = BashOperator(
    task_id='backup_files',
    bash_command=' '.join([rsync_files]),
    params={"item": "{{ ds_nodash }}"},
    dag=dag,
)














from airflow import DAG
from airflow.providers.ssh.operators.ssh_operator import SSHOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import os
import tarfile
import shutil
import subprocess

def copy_remote_directory():
    # SSHOperator to copy the remote directory to a local directory
    ssh_copy_command = """
    scp -r user@remote_server:/path/to/remote_directory /path/to/local_directory/{{ ds_nodash }}
    """
    return SSHOperator(
        task_id='copy_remote_directory',
        ssh_conn_id='your_ssh_connection_id',  # Configure your SSH connection in Airflow
        command=ssh_copy_command,
        dag=dag,
    )

def scan_and_extract_tar_files(ds, **kwargs):
    local_directory = f"/path/to/local_directory/{ds}"
    for root, _, files in os.walk(local_directory):
        for filename in files:
            if filename.endswith('.tar.gz'):
                tar_file_path = os.path.join(root, filename)
                extract_path = os.path.join(root, filename[:-7])  # Remove .tar.gz extension
                with tarfile.open(tar_file_path, 'r:gz') as tar:
                    tar.extractall(extract_path)
                # Git commit logic
                git_commit(extract_path)

def git_commit(directory):
    # Change to the directory containing extracted files
    os.chdir(directory)

    # Initialize a Git repository if it doesn't exist
    if not os.path.exists('.git'):
        subprocess.run(['git', 'init'])

    # Add all files to the Git repository
    subprocess.run(['git', 'add', '.'])

    # Commit the changes
    subprocess.run(['git', 'commit', '-m', 'Commit extracted files'])

dag = DAG(
    'extract_and_commit_files',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
)

copy_task = copy_remote_directory()

scan_and_extract_task = PythonOperator(
    task_id='scan_and_extract_tar_files',
    provide_context=True,
    python_callable=scan_and_extract_tar_files,
    dag=dag,
)

copy_task >> scan_and_extract_task


# Set task dependencies
backup_task




def scan_and_extract_tar_files(ds, **kwargs):
    local_directory = f"/path/to/local_directory/{ds}"
    for root, _, files in os.walk(local_directory):
        for filename in files:
            if filename.endswith('.tar.gz'):
                tar_file_path = os.path.join(root, filename)
                extract_path = os.path.join(root, filename[:-7])  # Remove .tar.gz extension
                with tarfile.open(tar_file_path, 'r:gz') as tar:
                    tar.extractall(extract_path)
                # Check if the extracted directory structure is 'prodbase/exe'
                if is_prodbase_exe_structure(extract_path):
                    # Git commit logic
                    git_commit(extract_path)

def is_prodbase_exe_structure(directory):
    # Check if the directory structure is 'prodbase/exe'
    return os.path.exists(os.path.join(directory, 'prodbase', 'exe'))


