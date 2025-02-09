
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.hooks.gcs_hook import GoogleCloudStorageHook
import json
from datetime import datetime

FILE_NAME = f'./test.json'
DOWNLOAD_NAME = f'./downloaded.json'

def save_data():
    with open(FILE_NAME, 'w') as f:
        json.dump({"name":"name", "age":10}, f)

def upload_file_func():
    save_data()
    hook = GoogleCloudStorageHook()
    source_bucket = 'airflow-test-source'
    source_object = '/data/test.json'
    hook.upload(source_bucket, source_object, FILE_NAME)

def copy_file_func():
    hook = GoogleCloudStorageHook()
    source_bucket = 'airflow-test-source'
    source_object = '/data/test.json'

    dest_bucket = 'airflow-test-dest'
    dest_object = 'test.json'
    hook.copy(source_bucket, source_object, dest_bucket, dest_object)

def download_file_func():
    hook = GoogleCloudStorageHook()
    dest_bucket = 'airflow-test-dest'
    dest_object = 'test.json'
    hook.download(dest_bucket, dest_object, DOWNLOAD_NAME)
    with open(DOWNLOAD_NAME) as json_file:
        data = json.load(json_file)
    print(data)

with DAG('gcs_examples', description='DAG', schedule_interval=None, start_date=datetime(2018, 11, 1)) as dag:

    upload_file	= PythonOperator(task_id='upload_file', python_callable=upload_file_func)
    copy_file	= PythonOperator(task_id='copy_file', python_callable=copy_file_func)
    download_file = PythonOperator(task_id='download_file', python_callable=download_file_func)
    upload_file >> copy_file >> download_file