from collections.abc import Generator

import snowflake.connector

from capstone_test.core.snowflake_client import get_connection


def get_db() -> Generator[snowflake.connector.SnowflakeConnection, None, None]:
    with get_connection() as conn:
        yield conn
