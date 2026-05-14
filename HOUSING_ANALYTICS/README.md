# HOUSING_ANALYTICS — dbt Project

dbt project for the Nashville Housing Affordability Analytics pipeline. All transformation lives here — Python handles extraction and loading only.

## Structure

```
HOUSING_ANALYTICS/
├── models/
│   ├── staging/           # 1:1 with RAW tables — light cleaning, type casting, column renaming
│   │   ├── _sources.yml   # Source freshness checks (warn >35d monthly, >400d annual)
│   │   ├── _staging.yml   # 29 tests
│   │   ├── stg_fred_cpi.sql
│   │   ├── stg_fred_permits.sql
│   │   ├── stg_zillow_zori.sql
│   │   ├── stg_bls_laus.sql
│   │   ├── stg_acs_estimates.sql  # GENERATOR expands annual → 12 monthly rows
│   │   └── stg_redfin.sql
│   └── marts/             # Business logic, joins, aggregations
│       ├── _marts.yml     # 16 tests
│       ├── mart_monthly_housing_metrics.sql
│       ├── mart_rent_burden.sql
│       ├── mart_supply_demand.sql
│       └── mart_affordability_index.sql
├── macros/
│   ├── generate_schema_name.sql  # Routes staging → STAGING, marts → MARTS
│   └── forward_fill.sql          # Window-function helper for gap-fill in marts
└── dbt_project.yml
```

## Common Commands

Run from the `HOUSING_ANALYTICS/` directory:

```bash
dbt debug                          # Verify Snowflake connection
dbt run --select staging           # All 6 staging models
dbt run --select marts             # All 4 mart models
dbt test                           # Full test suite (45 tests: 29 staging + 16 marts)
dbt docs generate && dbt docs serve
```

## Snowflake Target

- **Database:** `HOUSING_ANALYTICS`
- **Staging schema:** `STAGING` (views)
- **Marts schema:** `MARTS` (tables)
- **Warehouse:** `HOUSING_ANALYTICS_WH` (X-Small, auto-suspend 60s)

Profile is configured in `~/.dbt/profiles.yml` (gitignored). A local `profiles.yml` is also present in this directory for reference.

## Mart Descriptions

| Model | Grain | Key Metric |
|---|---|---|
| `mart_monthly_housing_metrics` | One row per month per geography | Master join spine |
| `mart_rent_burden` | One row per month, Davidson County | Rent burden %, 30% threshold flag |
| `mart_supply_demand` | One row per month, Davidson County / Nashville Metro | Permits vs. employment growth with lag columns |
| `mart_affordability_index` | One row per month, Davidson County | Composite 0–100 score (higher = less affordable) |

## Design Rules

- Staging models are views; mart models are tables.
- All Census variable codes (`B19013_001E` etc.) are decoded into human-readable column names in staging — never in Python or in mart queries.
- ACS annual data is expanded to monthly rows in `stg_acs_estimates` using `GENERATOR(rowcount => 12)`. Forward-filled months carry `is_forward_filled = true`.
- No business logic in Python — if it shapes or interprets data, it belongs here.
