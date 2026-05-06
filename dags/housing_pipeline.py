import shutil
import subprocess
from datetime import datetime

from airflow.decorators import dag, task

from capstone_test.pipeline import ingest, load

_DBT_DIR = "/opt/airflow/workspace/HOUSING_ANALYTICS"
_DBT = shutil.which("dbt") or "dbt"


@dag(
    dag_id="housing_pipeline",
    schedule="0 0 1 * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
)
def housing_pipeline() -> None:

    @task
    def ingest_and_load() -> None:
        load.run(ingest.run())

    @task
    def dbt_run() -> None:
        subprocess.run([_DBT, "run"], cwd=_DBT_DIR, check=True)

    @task
    def dbt_test() -> None:
        subprocess.run([_DBT, "test"], cwd=_DBT_DIR, check=True)

    ingest_and_load() >> dbt_run() >> dbt_test()


dag = housing_pipeline()
