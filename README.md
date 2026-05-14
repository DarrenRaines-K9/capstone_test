# Nashville Housing Affordability Analytics

A production-grade data engineering pipeline that tracks and visualizes housing affordability trends in Nashville, TN. The pipeline ingests data from six external APIs, loads into Snowflake, transforms with dbt, orchestrates with Airflow, and surfaces insights via a Streamlit dashboard.

**Analytical thesis:** Track the relationship between rent growth, labor market demand, housing supply, and affordability pressure in Nashville — with national CPI as a benchmark.

---

## Architecture

```
External APIs (FRED, BLS, Census, Zillow, Redfin)
        ↓
httpx.Client  (retry + backoff — core/http_client.py)
        ↓
Pydantic Validation  (core/schemas.py)
        ↓
Pandas DataFrames
        ↓
Snowflake RAW Schema  (upsert via core/snowflake_client.py)
        ↓
dbt Staging  (1:1 transforms, light cleaning)
        ↓
dbt Marts  (joins, aggregations, affordability index)
        ↓
Streamlit Dashboard / FastAPI
```

**Stack:** Python 3.12 · uv · httpx · pandas · pydantic · Snowflake · dbt-snowflake · Apache Airflow 3.2.1 · Streamlit · Plotly · Docker

---

## Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Docker Desktop (for Airflow)
- A Snowflake account with:
  - Database: `HOUSING_ANALYTICS`
  - Warehouse: `HOUSING_ANALYTICS_WH` (X-Small, auto-suspend 60s recommended)
  - Schemas: `RAW`, `STAGING`, `MARTS`
- API keys from:
  - [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)
  - [BLS](https://www.bls.gov/developers/home.htm)
  - [US Census](https://api.census.gov/data/key_signup.html)
  - Zillow and Redfin require no auth

---

## Getting Started

**1. Clone and configure environment**

```bash
cp .env.example .env
# Fill in .env with your API keys and Snowflake credentials
```

**2. Install dependencies**

```bash
uv sync
source .venv/bin/activate
```

**3. Run the pipeline locally**

```bash
# Full pipeline (ingest all sources + load to Snowflake)
python main.py

# Single source only
python main.py --source fred_cpi

# Individual stages
python -c "from capstone_test.pipeline.runner import run; run('ingest')"
python -c "from capstone_test.pipeline.runner import run; run('load')"
python -c "from capstone_test.pipeline.runner import run; run('dbt', step='staging')"
python -c "from capstone_test.pipeline.runner import run; run('dbt', step='marts')"
```

**4. Start Airflow (Docker)**

```bash
docker compose up -d
# Airflow UI → http://localhost:8080
```

**5. Run the Streamlit dashboard**

```bash
uv run streamlit run dashboard/app.py
# Dashboard → http://localhost:8501
```

**6. Run the FastAPI server (stretch goal)**

```bash
fastapi dev src/capstone_test/api/main.py
# API → http://localhost:8000 | Swagger UI → http://localhost:8000/docs
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `FRED_API_KEY` | FRED API key |
| `BLS_API_KEY` | BLS API v2 key |
| `CENSUS_API_KEY` | US Census API key |
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier |
| `SNOWFLAKE_USER` | Snowflake username |
| `SNOWFLAKE_PASSWORD` | Snowflake password |
| `SNOWFLAKE_DATABASE` | `HOUSING_ANALYTICS` |
| `SNOWFLAKE_WAREHOUSE` | `HOUSING_ANALYTICS_WH` |
| `SNOWFLAKE_ROLE` | Snowflake role |
| `OBSERVATION_START` | Earliest date to pull data (e.g. `2015-01-01`) |
| `ZILLOW_ZORI_URL` | Zillow ZORI CSV download URL |
| `AIRFLOW_UID` | UID for Airflow Docker user (typically `50000`) |

---

## Project Layout

```
capstone_test/
├── main.py                          # CLI entry point
├── Dockerfile                       # Extends airflow:3.2.1-python3.12
├── docker-compose.yml               # Airflow + Postgres
├── pyproject.toml                   # uv config, ruff linting rules
├── .env.example                     # Committed env template
│
├── src/capstone_test/
│   ├── core/                        # Shared utilities (written once, used everywhere)
│   │   ├── config.py               # Loads .env, exposes typed settings
│   │   ├── logging.py              # loguru with daily rotation, 30d retention
│   │   ├── schemas.py              # Pydantic validators for all 6 sources
│   │   ├── http_client.py          # Singleton httpx client with exponential backoff
│   │   └── snowflake_client.py     # Connection pool + upsert_dataframe() via MERGE
│   │
│   ├── config/
│   │   └── sources.py              # Source registry: extractor module, table, upsert keys
│   │
│   ├── sources/                     # One module per data source
│   │   ├── fred.py                 # FRED API → monthly CPI & permit series
│   │   ├── zillow.py               # Zillow ZORI CSV → asking rent by ZIP
│   │   ├── bls.py                  # BLS API v2 → employment & unemployment
│   │   ├── acs.py                  # Census ACS 5-year → income & rent burden
│   │   └── redfin.py               # Redfin S3 TSV → sale price, inventory, DOM
│   │
│   ├── pipeline/                    # Stage orchestrators
│   │   ├── args.py                 # CLI argument parser (--source, --stage, --step)
│   │   ├── ingest.py               # run(source_filter) → dict[str, DataFrame]
│   │   ├── load.py                 # run(dataframes) → upserts to Snowflake RAW
│   │   ├── dbt_runner.py           # run(step) → subprocess dbt command
│   │   └── runner.py               # Coordinates all stages
│   │
│   └── api/                         # FastAPI serving layer
│       ├── main.py                 # App entry point — lifespan, 5 routers registered
│       ├── deps.py                 # get_db() dependency wrapping get_connection()
│       ├── queries.py              # SQL functions returning typed Pydantic instances
│       ├── routers/                # One router per endpoint
│       │   ├── metrics.py         # GET /api/v1/metrics
│       │   ├── rent_burden.py     # GET /api/v1/rent-burden
│       │   ├── supply_demand.py   # GET /api/v1/supply-demand
│       │   ├── affordability.py   # GET /api/v1/affordability
│       │   └── summary.py         # GET /api/v1/summary
│       └── schemas/
│           └── responses.py       # Pydantic response models (one per mart)
│
├── .streamlit/
│   └── config.toml                  # Dark mode theme (navy bg, purple accent #7c6af7)
├── dags/
│   └── housing_pipeline.py          # Airflow DAG — monthly schedule, TaskFlow API
├── dashboard/
│   └── app.py                       # Streamlit dashboard — 5 pages, Plotly dark charts
├── HOUSING_ANALYTICS/               # dbt project (staging + marts complete, 45 tests passing)
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    ├── plan.md                      # Full project blueprint & design decisions
    ├── task.md                      # 12-phase task checklist with done conditions
    ├── fastapi_plan.md              # FastAPI implementation plan (Phase 12)
    └── grain_document.md            # Mart grain definitions and ACS forward-fill rules
```

---

## Data Sources

| Source | Module | Metric | Auth |
|---|---|---|---|
| FRED | `sources/fred.py` | National CPI, Nashville building permits | API key |
| Zillow ZORI | `sources/zillow.py` | Observed asking rent by ZIP | None |
| BLS LAUS | `sources/bls.py` | Employment, unemployment rate | API key |
| Census ACS | `sources/acs.py` | Median income, rent burden | API key |
| Redfin | `sources/redfin.py` | Sale price, inventory, days on market | None |

All extractors return a Snowflake-ready DataFrame with base columns: `source`, `observation_date`, `value`, `geography`, `unit`, `is_seasonally_adjusted`, `loaded_at`.

**Snowflake tables (RAW schema):** `FRED_CPI_RAW`, `FRED_PERMITS_RAW`, `ZILLOW_ZORI_RAW`, `BLS_LAUS_RAW`, `ACS_ESTIMATES_RAW`, `REDFIN_RAW`

---

## Design Principles

**One place for shared behavior.** HTTP retry, Snowflake connections, logging, config, and Pydantic schemas all live in `core/`. Never duplicated.

**All transformation in dbt.** Python handles extraction and loading only. No business logic, joins, or aggregations in Python code.

**One place for configuration.** Adding a new data source = one entry in `config/sources.py`.

---

## Current Status (Phase 12 in progress)

| Phase | Description | Status |
|---|---|---|
| 1–6 | Core layer, extractors, pipeline orchestrators, Docker | Complete |
| 7 | dbt project: 6 staging models + 4 mart models, 45 tests | Complete |
| 8 | Airflow DAG (`dags/housing_pipeline.py`) | Complete |
| 9 | Docker + Airflow 3.2.1 running, DAG verified end-to-end | Complete |
| 10 | Streamlit dashboard — 5 pages, dark mode, Plotly charts | Complete |
| 11 | Unit & integration tests | Not started |
| 12 | FastAPI — 5 endpoints built; Streamlit migrated to API; verification pending | Nearly complete |

See [docs/task.md](docs/task.md) for the full checklist and [docs/plan.md](docs/plan.md) for the project blueprint.