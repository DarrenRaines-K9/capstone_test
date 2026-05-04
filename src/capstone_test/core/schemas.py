import pandas as pd

_BASE_REQUIRED_COLUMNS = {
    "source",
    "observation_date",
    "value",
    "geography",
    "unit",
    "is_seasonally_adjusted",
    "loaded_at",
}

_BASE_NON_NULLABLE_COLUMNS = {
    "source", "observation_date", "geography", "unit", "loaded_at"
}


def _validate_base(observations: pd.DataFrame) -> None:
    missing_columns = _BASE_REQUIRED_COLUMNS - set(observations.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    for column_name in _BASE_NON_NULLABLE_COLUMNS:
        if observations[column_name].isnull().any():
            raise ValueError(f"Null values found in non-nullable column: {column_name}")


def validate_fred_observations(fred_observations: pd.DataFrame) -> pd.DataFrame:
    _validate_base(fred_observations)
    missing_columns = {"series_id"} - set(fred_observations.columns)
    if missing_columns:
        raise ValueError(f"FRED observations missing columns: {missing_columns}")
    if fred_observations["series_id"].isnull().any():
        raise ValueError("FRED observations contain null series_id")
    return fred_observations


def validate_bls_observations(bls_observations: pd.DataFrame) -> pd.DataFrame:
    _validate_base(bls_observations)
    missing_columns = {"series_id"} - set(bls_observations.columns)
    if missing_columns:
        raise ValueError(f"BLS observations missing columns: {missing_columns}")
    if bls_observations["series_id"].isnull().any():
        raise ValueError("BLS observations contain null series_id")
    return bls_observations


def validate_zillow_observations(zillow_observations: pd.DataFrame) -> pd.DataFrame:
    _validate_base(zillow_observations)
    missing_columns = {"region_id", "region_name"} - set(zillow_observations.columns)
    if missing_columns:
        raise ValueError(f"Zillow observations missing columns: {missing_columns}")
    if zillow_observations["region_id"].isnull().any():
        raise ValueError("Zillow observations contain null region_id")
    return zillow_observations


def validate_acs_observations(acs_observations: pd.DataFrame) -> pd.DataFrame:
    _validate_base(acs_observations)
    missing_columns = (
        {"survey_year", "variable_code", "variable_name"} - set(acs_observations.columns)
    )
    if missing_columns:
        raise ValueError(f"ACS observations missing columns: {missing_columns}")
    if acs_observations["survey_year"].isnull().any():
        raise ValueError("ACS observations contain null survey_year")
    return acs_observations


def validate_redfin_observations(redfin_observations: pd.DataFrame) -> pd.DataFrame:
    _validate_base(redfin_observations)
    missing_columns = {"region_id", "metric_name"} - set(redfin_observations.columns)
    if missing_columns:
        raise ValueError(f"Redfin observations missing columns: {missing_columns}")
    if redfin_observations["region_id"].isnull().any():
        raise ValueError("Redfin observations contain null region_id")
    return redfin_observations
