import importlib

import pandas as pd

from capstone_test.config.sources import SOURCES
from capstone_test.core.logging import logger


def run(source_filter: str | None = None) -> dict[str, pd.DataFrame]:
    sources_to_run = (
        {source_filter: SOURCES[source_filter]}
        if source_filter
        else SOURCES
    )

    ingested_dataframes: dict[str, pd.DataFrame] = {}

    for source_name, source_config in sources_to_run.items():
        logger.info(f"Ingest: starting {source_name}")
        try:
            extractor_module = importlib.import_module(source_config["extractor_module"])
            source_dataframe = extractor_module.extract(**source_config["extractor_kwargs"])
            ingested_dataframes[source_name] = source_dataframe
            logger.info(f"Ingest: {source_name} complete — {len(source_dataframe)} rows")
        except Exception as extraction_error:
            logger.error(f"Ingest: {source_name} failed — {extraction_error}")

    logger.info(
        f"Ingest complete: {len(ingested_dataframes)}/{len(sources_to_run)} sources succeeded"
    )
    return ingested_dataframes