SOURCES: dict[str, dict] = {
    "fred_cpi": {
        "extractor_module": "capstone_test.sources.fred",
        "target_table": "FRED_CPI_RAW",
        "schema": "RAW",
        "upsert_keys": ["observation_date", "series_id"],
        "extractor_kwargs": {"series_id": "CUSR0000SEHA"},
    },
    "fred_permits": {
        "extractor_module": "capstone_test.sources.fred",
        "target_table": "FRED_PERMITS_RAW",
        "schema": "RAW",
        "upsert_keys": ["observation_date", "series_id"],
        "extractor_kwargs": {"series_id": "NASH947BPPRIVSA"},
    },
    "zillow_zori": {
        "extractor_module": "capstone_test.sources.zillow",
        "target_table": "ZILLOW_ZORI_RAW",
        "schema": "RAW",
        "upsert_keys": ["observation_date", "region_id"],
        "extractor_kwargs": {},
    },
    "bls_laus": {
        "extractor_module": "capstone_test.sources.bls",
        "target_table": "BLS_LAUS_RAW",
        "schema": "RAW",
        "upsert_keys": ["observation_date", "series_id"],
        "extractor_kwargs": {
            "series_ids": [
                "LAUCN470370000000003",
                "LAUCN470370000000004",
                "LAUCN470370000000006",
            ]
        },
    },
    "acs_estimates": {
        "extractor_module": "capstone_test.sources.acs",
        "target_table": "ACS_ESTIMATES_RAW",
        "schema": "RAW",
        "upsert_keys": ["survey_year", "geography", "variable_code"],
        "extractor_kwargs": {
            "state": "47",
            "county": "037",
            "variables": ["B19013_001E", "B25064_001E", "B25070_001E"],
        },
    },
    "redfin": {
        "extractor_module": "capstone_test.sources.redfin",
        "target_table": "REDFIN_RAW",
        "schema": "RAW",
        "upsert_keys": ["observation_date", "region_id", "metric_name"],
        "extractor_kwargs": {},
    },
}
