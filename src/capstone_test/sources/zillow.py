import io

import pandas as pd

from capstone_test.core import config
from capstone_test.core.http_client import get_with_retry
from capstone_test.core.logging import logger
from capstone_test.core.schemas import validate_zillow_observations


_METADATA_COLUMNS = [
    "RegionID", "SizeRank", "RegionName", "RegionType",
    "StateName", "State", "City", "Metro", "CountyName",
]

_NASHVILLE_ZIP_CODES = {
    "37201", "37203", "37204", "37205", "37206", "37207", "37208",
    "37209", "37210", "37211", "37212", "37213", "37214", "37215",
    "37216", "37217", "37218", "37219", "37220", "37221", "37228",
}


def extract() -> pd.DataFrame:
    logger.info("Zillow: downloading ZORI ZIP-code CSV")
    response = get_with_retry(config.ZILLOW_ZORI_URL)

    zori_wide = pd.read_csv(io.BytesIO(response.content))
    nashville_zori_wide = zori_wide[
        zori_wide["RegionName"].astype(str).isin(_NASHVILLE_ZIP_CODES)
    ].copy()

    if nashville_zori_wide.empty:
        raise ValueError("No Nashville ZIP codes found in Zillow ZORI data")

    date_columns = [
        col for col in nashville_zori_wide.columns
        if col not in _METADATA_COLUMNS
        and col >= config.OBSERVATION_START.isoformat()[:7]
    ]

    nashville_zori_long = nashville_zori_wide.melt(
        id_vars=["RegionID", "RegionName"],
        value_vars=date_columns,
        var_name="observation_date",
        value_name="value",
    )

    nashville_zori_long = nashville_zori_long.dropna(subset=["value"])
    nashville_zori_long["observation_date"] = pd.to_datetime(
        nashville_zori_long["observation_date"]
    ).dt.date
    nashville_zori_long["region_id"] = nashville_zori_long["RegionID"].astype(str)
    nashville_zori_long["region_name"] = nashville_zori_long["RegionName"].astype(str)
    nashville_zori_long["source"] = "Zillow"
    nashville_zori_long["geography"] = "Nashville Metro, TN"
    nashville_zori_long["unit"] = "USD"
    nashville_zori_long["is_seasonally_adjusted"] = True
    nashville_zori_long["loaded_at"] = pd.Timestamp.utcnow()
    nashville_zori_long = nashville_zori_long.drop(columns=["RegionID", "RegionName"])

    logger.info(
        f"Zillow ZORI: {len(nashville_zori_long)} observations "
        f"for {nashville_zori_long['region_id'].nunique()} ZIP codes"
    )
    return validate_zillow_observations(nashville_zori_long)
