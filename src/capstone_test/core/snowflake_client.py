from contextlib import contextmanager
from typing import Generator

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

from capstone_test.core.config import (
    SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_DATABASE,
    SNOWFLAKE_PASSWORD,
    SNOWFLAKE_ROLE,
    SNOWFLAKE_USER,
    SNOWFLAKE_WAREHOUSE,
)
from capstone_test.core.logging import logger


@contextmanager
def get_connection() -> Generator[snowflake.connector.SnowflakeConnection, None, None]:
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        database=SNOWFLAKE_DATABASE,
        warehouse=SNOWFLAKE_WAREHOUSE,
        role=SNOWFLAKE_ROLE,
    )
    try:
        yield conn
    finally:
        conn.close()


def upsert_dataframe(
    df: pd.DataFrame,
    table: str,
    schema: str,
    upsert_keys: list[str],
) -> int:
    df = df.copy().reset_index(drop=True)
    df.columns = df.columns.str.upper()
    upsert_keys = [k.upper() for k in upsert_keys]
    df = df.drop_duplicates(subset=upsert_keys, keep="last")
    staging = f"{table.upper()}_STAGING"

    db = SNOWFLAKE_DATABASE
    fq_schema = f"{db}.{schema}"

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {fq_schema}")
        cur.execute(f"DROP TABLE IF EXISTS {fq_schema}.{staging}")

        write_pandas(
            conn,
            df,
            staging,
            database=db,
            schema=schema,
            auto_create_table=True,
            overwrite=True,
            table_type="transient",
            use_logical_type=True,
        )

        cur.execute(
            f"CREATE TRANSIENT TABLE IF NOT EXISTS {fq_schema}.{table} "
            f"LIKE {fq_schema}.{staging}"
        )

        cols = df.columns.tolist()
        non_key_cols = [c for c in cols if c not in upsert_keys]
        match_cond = " AND ".join(f't."{k}" = s."{k}"' for k in upsert_keys)
        insert_cols = ", ".join(f'"{c}"' for c in cols)
        insert_vals = ", ".join(f's."{c}"' for c in cols)

        update_clause = (
            "WHEN MATCHED THEN UPDATE SET "
            + ", ".join(f't."{c}" = s."{c}"' for c in non_key_cols)
            if non_key_cols
            else ""
        )

        cur.execute(f"""
            MERGE INTO {fq_schema}.{table} AS t
            USING {fq_schema}.{staging} AS s
            ON {match_cond}
            {update_clause}
            WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
        """)

        cur.execute(f"DROP TABLE IF EXISTS {fq_schema}.{staging}")

        logger.info(f"Upserted {len(df)} rows into {fq_schema}.{table}")
        return len(df)