import pandas as pd

from capstone_test.core import config
from capstone_test.core.http_client import get_client
from capstone_test.core.logging import logger
from capstone_test.core.schemas import validate_bls_observations

_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

_MEASURE_CODE_TO_UNIT = {
    "03": "unemployment_rate",
    "04": "unemployment_count",
    "06": "labor_force",
}


def extract(series_ids: list[str]) -> pd.DataFrame:
    logger.info(f"BLS: extracting {len(series_ids)} LAUS series")

    http_client = get_client()
    response = http_client.post(
        _API_URL,
        json={
            "seriesid": series_ids,
            "startyear": str(config.OBSERVATION_START.year),
            "endyear": str(pd.Timestamp.now().year),
            "registrationkey": config.BLS_API_KEY,
        },
    )
    response.raise_for_status()

    payload = response.json()
    if payload["status"] != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API error: {payload.get('message', payload['status'])}")

    observation_rows = []
    for series_result in payload["Results"]["series"]:
        series_id = series_result["seriesID"]
        measure_code = series_id[-2:]
        unit = _MEASURE_CODE_TO_UNIT.get(measure_code, "unknown")

        for period_observation in series_result["data"]:
            period_code = period_observation["period"]
            if not period_code.startswith("M") or period_code == "M13":
                continue

            month_number = int(period_code[1:])
            raw_value = period_observation["value"]

            observation_rows.append({
                "series_id": series_id,
                "observation_date": pd.Timestamp(
                    year=int(period_observation["year"]),
                    month=month_number,
                    day=1,
                ).date(),
                "value": float(raw_value) if raw_value not in ("-", "") else None,
                "source": "BLS",
                "geography": "Davidson County, TN",
                "unit": unit,
                "is_seasonally_adjusted": False,
                "loaded_at": pd.Timestamp.utcnow(),
            })

    bls_observations = pd.DataFrame(observation_rows)
    logger.info(f"BLS: {len(bls_observations)} observations across {len(series_ids)} series")
    return validate_bls_observations(bls_observations)
