import pandas as pd

from capstone_test.core import config
from capstone_test.core.http_client import get_with_retry
from capstone_test.core.logging import logger
from capstone_test.core.schemas import validate_fred_observations

_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def extract(series_id: str) -> pd.DataFrame:
    logger.info(f"FRED: extracting series {series_id}")

    response = get_with_retry(
        _BASE_URL,
        params={
            "series_id": series_id,
            "api_key": config.FRED_API_KEY,
            "observation_start": config.OBSERVATION_START.isoformat(),
            "file_type": "json",
        },
    )

    raw_observations = pd.DataFrame(response.json()["observations"])[["date", "value"]]

    # FRED encodes missing values as "." — drop them before casting
    valid_observations = raw_observations[raw_observations["value"] != "."].copy()
    valid_observations["value"] = pd.to_numeric(valid_observations["value"])

    valid_observations["series_id"] = series_id
    valid_observations["source"] = "FRED"
    valid_observations["observation_date"] = pd.to_datetime(valid_observations["date"]).dt.date
    valid_observations["geography"] = "Nashville, TN"
    valid_observations["unit"] = "index"
    valid_observations["is_seasonally_adjusted"] = True
    valid_observations["loaded_at"] = pd.Timestamp.utcnow()
    valid_observations = valid_observations.drop(columns=["date"])

    logger.info(f"FRED {series_id}: {len(valid_observations)} observations")
    return validate_fred_observations(valid_observations)
