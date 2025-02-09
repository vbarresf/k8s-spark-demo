import logging
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocDeleteClusterOperator,
)
from airflow.utils import trigger_rule
from utils.dataproc_manager import DataprocManager

schedule = None
cluster_name = "sdg-demo-train-model"
PROJECT = "sdg-demo-448621"
REGION = "us-central1"
CLUSTER_CONFIG = {
    "master_config": {
        "num_instances": 1,
        "machine_type_uri": "n1-standard-4",
        "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 1024},
    },
    "worker_config": {
        "num_instances": 2,
        "machine_type_uri": "n1-standard-4",
        "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 1024},
    },
    # came from datastax to help resolve the SSL issues
    "software_config": {
        "properties": {
            "dataproc:dataproc.conscrypt.provider.enable": "false"
        }
    }
}

def obtain_dataproc(_config):
    logging.info(f"Loading config for :{_config}")
    dataproc_manager = DataprocManager(_config)
    return dataproc_manager.get_dataproc()


def get_config():
    data = {
        'DagName': 'TrainModel',
        'DataprocConf': 'standard',
        'Schedule': None,
        'DataProcName': 'sdg-demo-train-model'
    }
    return data

with DAG(
        "TrainModel",
        default_args={
            "start_date": datetime(2020, 11, 18),
            "email_on_failure": False,
            "email_on_retry": False,
            "retries": 0,
            "retry_delay": timedelta(minutes=5),
            "project_id": PROJECT,
            "region": REGION,
        },
        schedule= schedule,
        params=
        {
        },
        tags=['Train-model'],
) as dag:

    create_dataproc_cluster = DataprocCreateClusterOperator(
            task_id="create_dataproc_cluster",
            cluster_name=cluster_name,
            cluster_config=CLUSTER_CONFIG,
            timeout=3600
    )

    run_spark_job = DataprocSubmitJobOperator(
            task_id="run_train_model",
            job={
                "spark_job": {
                    "main_python_file_uri": "train_model.py",
                    "properties": {
                        "spark.gcs-dataset-path": "gs://sdg-demo-train/dataset",
                        "spark.gcs-model-path": "gs://sdg-demo-train/model",
                        "spark.gcp-project": "sdg-demo-448621",
                    }
                }
            }
    )

    delete_dataproc_cluster = DataprocDeleteClusterOperator(
            task_id="delete_dataproc_cluster",
            cluster_name=cluster_name,
            trigger_rule=trigger_rule.TriggerRule.ALL_DONE
    )

    create_dataproc_cluster >> run_spark_job >> delete_dataproc_cluster