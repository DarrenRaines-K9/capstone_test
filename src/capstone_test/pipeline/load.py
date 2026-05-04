import pandas as pd

from capstone_test.config.sources import SOURCES
from capstone_test.core.logging import logger
from capstone_test.core.snowflake_client import upsert_dataframe


def run(ingested_dataframes: dict[str, pd.DataFrame]) -> None:
    for source_name, source_dataframe in ingested_dataframes.items():
        source_config = SOURCES[source_name]
        logger.info(
            f"Load: writing {len(source_dataframe)} rows from {source_name} "
            f"to {source_config['schema']}.{source_config['target_table']}"
        )
        try:
            rows_upserted = upsert_dataframe(
                source_dataframe,
                table=source_config["target_table"],
                schema=source_config["schema"],
                upsert_keys=source_config["upsert_keys"],
            )
            logger.info(f"Load: {source_name} — {rows_upserted} rows upserted")
        except Exception as load_error:
            logger.error(f"Load: {source_name} failed — {load_error}")
            raise