import argparse


def parse_pipeline_args() -> argparse.Namespace:
    argument_parser = argparse.ArgumentParser(description="Nashville Housing Analytics pipeline")
    argument_parser.add_argument(
        "--source",
        default=None,
        help="Single source name to ingest (e.g. fred_cpi). Omit to run all sources.",
    )
    return argument_parser.parse_args()