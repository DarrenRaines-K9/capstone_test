import time

from capstone_test.core.logging import logger
from capstone_test.pipeline import dbt_runner, ingest, load


def run(stage: str, source: str | None = None, step: str | None = None) -> None:
    pipeline_start_time = time.time()
    logger.info(f"Pipeline starting — stage={stage}")

    ingested_dataframes = {}

    if stage in ("ingest", "load", "all"):
        ingested_dataframes = ingest.run(source_filter=source)

    if stage in ("load", "all"):
        load.run(ingested_dataframes)

    if stage == "dbt":
        dbt_runner.run(step)

    elapsed_seconds = time.time() - pipeline_start_time
    logger.info(f"Pipeline complete — stage={stage} — {elapsed_seconds:.1f}s")