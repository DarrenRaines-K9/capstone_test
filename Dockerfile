FROM apache/airflow:2.9.0-python3.12

RUN pip install --no-cache-dir \
    httpx \
    pandas \
    "pydantic>=2" \
    python-dotenv \
    loguru \
    snowflake-connector-python \
    dbt-snowflake \
    streamlit \
    psycopg2-binary