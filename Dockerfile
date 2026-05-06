FROM apache/airflow:3.2.1-python3.12


RUN pip install --no-cache-dir \
    httpx \
    pandas \
    python-dotenv \
    loguru \
    snowflake-connector-python \
    dbt-snowflake \
    pydantic-settings \