import os
from datetime import date

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

FRED_API_KEY: str = os.environ["FRED_API_KEY"]
BLS_API_KEY: str = os.environ["BLS_API_KEY"]
CENSUS_API_KEY: str = os.environ["CENSUS_API_KEY"]

SNOWFLAKE_ACCOUNT: str = os.environ["SNOWFLAKE_ACCOUNT"]
SNOWFLAKE_USER: str = os.environ["SNOWFLAKE_USER"]
SNOWFLAKE_PASSWORD: str = os.environ["SNOWFLAKE_PASSWORD"]
SNOWFLAKE_DATABASE: str = os.environ.get("SNOWFLAKE_DATABASE", "HOUSING_ANALYTICS")
SNOWFLAKE_WAREHOUSE: str = os.environ.get("SNOWFLAKE_WAREHOUSE", "HOUSING_ANALYTICS_WH")
SNOWFLAKE_ROLE: str = os.environ["SNOWFLAKE_ROLE"]

OBSERVATION_START: date = date.fromisoformat(
    os.environ.get("OBSERVATION_START", "2015-01-01")
)

ZILLOW_ZORI_URL: str = os.environ["ZILLOW_ZORI_URL"]