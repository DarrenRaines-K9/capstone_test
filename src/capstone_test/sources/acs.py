import httpx
import pandas as pd

from capstone_test.core import config
from capstone_test.core.http_client import get_with_retry
from capstone_test.core.logging import logger
from capstone_test.core.schemas import validate_acs_observations

_ACS_API_BASE_URL = "https://api.census.gov/data/{year}/acs/acs5"
_LATEST_AVAILABLE_ACS_YEAR = 2023

_VARIABLE_CODE_TO_NAME = {
    "B19013_001E": "median_household_income",
    "B25064_001E": "median_gross_rent",
    "B25070_001E": "gross_rent_pct_of_income",
}

_CENSUS_NULL_VALUES = {"-1", "-666666666", None}


def _parse_raw_value(raw_value: str | None) -> float | None:
    if raw_value in _CENSUS_NULL_VALUES:
        return None
    try:
        return float(raw_value)
    except (ValueError, TypeError):
        return None


def _build_observation_row(
    survey_year: int,
    geography_name: str,
    variable_code: str,
    raw_value: str | None,
) -> dict:
    return {
        "survey_year": survey_year,
        "observation_date": pd.Timestamp(year=survey_year, month=1, day=1).date(),
        "geography": geography_name,
        "variable_code": variable_code,
        "variable_name": _VARIABLE_CODE_TO_NAME.get(variable_code, variable_code),
        "value": _parse_raw_value(raw_value),
        "source": "ACS 5-Year",
        "unit": "USD" if variable_code.endswith("E") else "percent",
        "is_seasonally_adjusted": False,
        "loaded_at": pd.Timestamp.utcnow(),
    }


def extract(state: str, county: str, variables: list[str]) -> pd.DataFrame:
    logger.info(f"ACS: extracting {variables} for state={state} county={county}")

    start_year = config.OBSERVATION_START.year
    end_year = min(pd.Timestamp.now().year - 2, _LATEST_AVAILABLE_ACS_YEAR)
    observation_rows = []

    for survey_year in range(start_year, end_year + 1):
        url = _ACS_API_BASE_URL.format(year=survey_year)
        try:
            response = get_with_retry(
                url,
                params={
                    "get": ",".join(variables) + ",NAME",
                    "for": f"county:{county}",
                    "in": f"state:{state}",
                    "key": config.CENSUS_API_KEY,
                },
            )
        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.NetworkError) as fetch_error:
            logger.warning(f"ACS: skipping {survey_year}: {fetch_error}")
            continue

        raw_rows = response.json()
        if len(raw_rows) < 2:
            logger.warning(f"ACS: no data returned for {survey_year}")
            continue

        column_headers = raw_rows[0]
        data_row = raw_rows[1]
        geography_name = data_row[column_headers.index("NAME")]

        for variable_code in variables:
            if variable_code not in column_headers:
                continue
            raw_value = data_row[column_headers.index(variable_code)]
            observation_rows.append(
                _build_observation_row(survey_year, geography_name, variable_code, raw_value)
            )

    acs_observations = pd.DataFrame(observation_rows)
    logger.info(
        f"ACS: {len(acs_observations)} observations "
        f"across {end_year - start_year + 1} survey years"
    )
    return validate_acs_observations(acs_observations)