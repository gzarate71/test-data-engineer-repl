
"""
* project_id is the Google Cloud Project ID to use for the Cloud Dataproc Serverless.
* bucket_name is the URI of a bucket where the main python file of the workload (replicate_cdc.py) is located.
* phs_cluster is the Persistent History Server cluster name.
* image_name is the name and tag of the custom container image (image:tag).
* metastore_cluster is the Dataproc Metastore service name.
* region_name is the region where the Dataproc Metastore service is located.
"""

import datetime

from airflow import models
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateBatchOperator,
    DataprocDeleteBatchOperator,
    DataprocGetBatchOperator,
    DataprocListBatchesOperator,
)
from airflow.utils.dates import days_ago

PROJECT_ID = "{{ var.value.project_id }}"
REGION = "{{ var.value.region_name}}"
BUCKET = "{{ var.value.bucket_name }}"
PHS_CLUSTER = "{{ var.value.phs_cluster }}"
METASTORE_CLUSTER = "{{var.value.metastore_cluster}}"
DOCKER_IMAGE = "{{var.value.image_name}}"

PYTHON_FILE_LOCATION = "gs://{{var.value.bucket_name }}/replicate_cdc.py"
# for e.g.  "gs//my-bucket/replicate_cdc.py"
# Start a single node Dataproc Cluster for viewing Persistent History of Spark jobs
PHS_CLUSTER_PATH = "projects/{{ var.value.project_id }}/regions/{{ var.value.region_name}}/clusters/{{ var.value.phs_cluster }}"
# for e.g. projects/my-project/regions/my-region/clusters/my-cluster"
SPARK_BIGQUERY_JAR_FILE = "gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar"
# use this for those pyspark jobs that need a spark-bigquery connector
# https://cloud.google.com/dataproc/docs/tutorials/bigquery-connector-spark-example
# Start a Dataproc MetaStore Cluster
METASTORE_SERVICE_LOCATION = "projects/{{var.value.project_id}}/locations/{{var.value.region_name}}/services/{{var.value.metastore_cluster }}"
# for e.g. projects/my-project/locations/my-region/services/my-cluster
CUSTOM_CONTAINER = "us.gcr.io/{{var.value.project_id}}/{{ var.value.image_name}}"
# for e.g. "us.gcr.io/my-project/quickstart-image",

default_args = {
    # Tell airflow to start one day ago, so that it runs as soon as you upload it
    "start_date": days_ago(1),
    "project_id": PROJECT_ID,
    "region": REGION,
}
with models.DAG(
    "run_dataproc_job",  # The id you will see in the DAG airflow page
    default_args=default_args,  # The interval with which to schedule the DAG
    schedule_interval=datetime.timedelta(minutes=5),  # Override to match your needs
) as dag:
    create_batch = DataprocCreateBatchOperator(
        task_id="batch_create",
        batch={
            "pyspark_batch": {
                "main_python_file_uri": PYTHON_FILE_LOCATION,
                "jar_file_uris": [SPARK_BIGQUERY_JAR_FILE],
            },
            "environment_config": {
                "peripherals_config": {
                    "spark_history_server_config": {
                        "dataproc_cluster": PHS_CLUSTER_PATH,
                    },
                },
            },
        },
        batch_id="batch-create-phs",
    )
    list_batches = DataprocListBatchesOperator(
        task_id="list-all-batches",
    )

    get_batch = DataprocGetBatchOperator(
        task_id="get_batch",
        batch_id="batch-create-phs",
    )
    delete_batch = DataprocDeleteBatchOperator(
        task_id="delete_batch",
        batch_id="batch-create-phs",
    )
    create_batch >> list_batches >> get_batch >> delete_batch
