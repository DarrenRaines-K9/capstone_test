import io

import pandas as pd

from capstone_test.core import config
from capstone_test.core.http_client import get_with_retry
from capstone_test.core.logging import logger
from capstone_test.core.schemas import validate_redfin_observations

_REDFIN_METRO_TSV_URL = (
    "https://redfin-public-data.s3.us-west-2.amazonaws.com"
    "/redfin_market_tracker/redfin_metro_market_tracker.tsv000.gz"
)

_NASHVILLE_METRO_FILTER = "Nashville, TN"

_REDFIN_METRIC_COLUMNS = [
    "median_sale_price",
    "median_list_price",
    "homes_sold",
    "inventory",
    "median_dom",
    "avg_sale_to_list",
]

_METRIC_UNIT = {
    "median_sale_price": "USD",
    "median_list_price": "USD",
    "homes_sold": "count",
    "inventory": "count",
    "median_dom": "days",
    "avg_sale_to_list": "ratio",
}


def extract() -> pd.DataFrame:
    logger.info("Redfin: downloading metro market tracker")
    response = get_with_retry(_REDFIN_METRO_TSV_URL)

    all_metro_data = pd.read_csv(
        io.BytesIO(response.content),
        sep="\t",
        compression="gzip",
        low_memory=False,
    )
    all_metro_data.columns = all_metro_data.columns.str.lower()

    nashville_raw = all_metro_data[
        all_metro_data["region"].str.contains(_NASHVILLE_METRO_FILTER, na=False)
        & (all_metro_data["property_type"] == "All Residential")
    ].copy()

    if nashville_raw.empty:
        raise ValueError(f"No Redfin data found for {_NASHVILLE_METRO_FILTER}")

    observation_start_str = config.OBSERVATION_START.isoformat()
    nashville_in_window = nashville_raw[
        nashville_raw["period_begin"] >= observation_start_str
    ].copy()

    available_metric_columns = [
        col for col in _REDFIN_METRIC_COLUMNS if col in nashville_in_window.columns
    ]

    observation_rows = []
    for _, source_row in nashville_in_window.iterrows():
        observation_date = pd.to_datetime(source_row["period_begin"]).date()
        region_id = str(source_row["table_id"])
        for metric_name in available_metric_columns:
            raw_value = source_row[metric_name]
            observation_rows.append({
                "observation_date": observation_date,
                "region_id": region_id,
                "metric_name": metric_name,
                "value": float(raw_value) if pd.notna(raw_value) else None,
                "geography": _NASHVILLE_METRO_FILTER,
                "source": "Redfin",
                "unit": _METRIC_UNIT.get(metric_name, "count"),
                "is_seasonally_adjusted": False,
                "loaded_at": pd.Timestamp.utcnow(),
            })

    redfin_observations = pd.DataFrame(observation_rows)
    logger.info(f"Redfin: {len(redfin_observations)} observations")
    return validate_redfin_observations(redfin_observations)
