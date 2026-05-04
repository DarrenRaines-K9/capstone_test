from capstone_test.core.logging import logger
from capstone_test.pipeline.args import parse_pipeline_args
from capstone_test.pipeline.ingest import run as run_ingest
from capstone_test.pipeline.load import run as run_load


def main() -> None:
    parsed_args = parse_pipeline_args()

    logger.info("Pipeline: starting")

    logger.info("Pipeline: ingest")
    ingested_data = run_ingest(source_filter=parsed_args.source)

    logger.info("Pipeline: load")
    run_load(ingested_data)

    logger.info("Pipeline: complete")


if __name__ == "__main__":
    main()