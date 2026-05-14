import os

import httpx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE_URL")

# ── Plotly dark theme matching Streamlit dark background ─────────────────────
_BG = "#0e1117"
_PANEL = "#1a1f2e"
_TEXT = "#e8eaf6"
_GRID = "#2a3040"
_ACCENT = "#7c6af7"
_GREEN = "#4caf87"
_AMBER = "#f5a623"
_RED = "#ef5350"

_PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=_PANEL,
    plot_bgcolor=_PANEL,
    font=dict(color=_TEXT, family="sans-serif"),
    xaxis=dict(gridcolor=_GRID, linecolor=_GRID, showgrid=True),
    yaxis=dict(gridcolor=_GRID, linecolor=_GRID, showgrid=True),
    margin=dict(l=12, r=12, t=36, b=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=_TEXT)),
    hovermode="x unified",
)


def _fig(**kwargs) -> go.Figure:
    layout = {**_PLOTLY_LAYOUT, **kwargs}
    return go.Figure(layout=go.Layout(**layout))


# ── Data loading via FastAPI ──────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Loading housing metrics…")
def load_monthly_metrics() -> pd.DataFrame:
    resp = httpx.get(f"{API_BASE}/api/v1/metrics")
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    return df


@st.cache_data(ttl=3600, show_spinner="Loading rent burden…")
def load_rent_burden() -> pd.DataFrame:
    resp = httpx.get(f"{API_BASE}/api/v1/rent-burden")
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    return df


@st.cache_data(ttl=3600, show_spinner="Loading supply/demand…")
def load_supply_demand() -> pd.DataFrame:
    resp = httpx.get(f"{API_BASE}/api/v1/supply-demand")
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    return df


@st.cache_data(ttl=3600, show_spinner="Loading affordability index…")
def load_affordability() -> pd.DataFrame:
    resp = httpx.get(f"{API_BASE}/api/v1/affordability")
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    return df


# ── Helpers ──────────────────────────────────────────────────────────────────
def _date_filter(df: pd.DataFrame, year_range: tuple[int, int]) -> pd.DataFrame:
    lo = pd.Timestamp(year=year_range[0], month=1, day=1)
    hi = pd.Timestamp(year=year_range[1], month=12, day=31)
    return df[(df["observation_date"] >= lo) & (df["observation_date"] <= hi)]


def _yoy(series: pd.Series) -> pd.Series:
    return series.pct_change(12).mul(100).round(2)


def _kpi(col, label: str, value: str, delta: str | None = None, delta_color: str = "normal") -> None:
    col.metric(label, value, delta, delta_color=delta_color)


# ── Pages ────────────────────────────────────────────────────────────────────
def page_overview(mdf: pd.DataFrame, rdf: pd.DataFrame, adf: pd.DataFrame, year_range: tuple[int, int]) -> None:
    st.header("Nashville Housing — Overview")

    latest = mdf.dropna(subset=["zip_median_asking_rent_usd"]).iloc[-1]
    prev_yr = mdf[
        mdf["observation_date"] == latest["observation_date"] - pd.DateOffset(years=1)
    ]

    rent_now = latest["zip_median_asking_rent_usd"]
    rent_prev = prev_yr["zip_median_asking_rent_usd"].iloc[0] if not prev_yr.empty else None
    rent_delta = f"{((rent_now - rent_prev) / rent_prev * 100):+.1f}% YoY" if rent_prev else None

    burden_latest = rdf.dropna(subset=["rent_burden_pct"]).iloc[-1]
    afford_latest = adf.dropna(subset=["affordability_index"]).iloc[-1]

    permits_latest = mdf.dropna(subset=["metro_permit_count"]).iloc[-1]
    permits_12m = mdf.dropna(subset=["metro_permit_count"]).tail(12)["metro_permit_count"].sum()

    c1, c2, c3, c4 = st.columns(4)
    _kpi(c1, "Median Asking Rent", f"${rent_now:,.0f}/mo", rent_delta)
    _kpi(c2, "Rent Burden", f"{burden_latest['rent_burden_pct']:.1f}%",
         "Above 30% threshold" if burden_latest["is_above_30_pct_threshold"] else "Below 30% threshold",
         delta_color="inverse" if burden_latest["is_above_30_pct_threshold"] else "normal")
    _kpi(c3, "Affordability Index", f"{afford_latest['affordability_index']:.0f} / 100",
         "Higher = less affordable", delta_color="off")
    _kpi(c4, "Permits (trailing 12mo)", f"{permits_12m:,.0f}")

    st.divider()

    mf = _date_filter(mdf, year_range)
    fig = _fig(title="Median Asking Rent vs. National CPI — Indexed to 2015")

    rent_valid = mf.dropna(subset=["zip_median_asking_rent_usd"])
    cpi_valid = mf.dropna(subset=["national_cpi_index"])

    rent_base = rent_valid["zip_median_asking_rent_usd"].iloc[0] if not rent_valid.empty else None
    cpi_base = cpi_valid["national_cpi_index"].iloc[0] if not cpi_valid.empty else None

    if rent_base:
        fig.add_trace(go.Scatter(
            x=rent_valid["observation_date"],
            y=(rent_valid["zip_median_asking_rent_usd"] / rent_base * 100).round(1),
            name="Nashville Rent (ZORI)",
            line=dict(color=_ACCENT, width=2),
        ))
    if cpi_base:
        fig.add_trace(go.Scatter(
            x=cpi_valid["observation_date"],
            y=(cpi_valid["national_cpi_index"] / cpi_base * 100).round(1),
            name="National Rent CPI",
            line=dict(color=_AMBER, width=2, dash="dot"),
        ))

    fig.update_yaxes(title_text="Index (2015 = 100)")
    st.plotly_chart(fig, use_container_width=True)


def page_rent_trends(mdf: pd.DataFrame, year_range: tuple[int, int]) -> None:
    st.header("Rent Trends")
    mf = _date_filter(mdf, year_range)

    fig = _fig(title="Median Asking Rent — Nashville ZIP Aggregate (Zillow ZORI)")
    rent = mf.dropna(subset=["zip_median_asking_rent_usd"])
    fig.add_trace(go.Scatter(
        x=rent["observation_date"],
        y=rent["zip_median_asking_rent_usd"],
        name="Median Asking Rent",
        line=dict(color=_ACCENT, width=2.5),
        fill="tozeroy",
        fillcolor="rgba(124,106,247,0.08)",
    ))
    fig.update_yaxes(title_text="USD / month", tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    fig2 = _fig(title="Rent YoY Growth vs. National CPI YoY Growth")
    rent_yoy = _yoy(rent.set_index("observation_date")["zip_median_asking_rent_usd"]).reset_index()
    rent_yoy.columns = ["observation_date", "rent_yoy"]
    rent_yoy = rent_yoy.dropna()

    cpi = mf.dropna(subset=["national_cpi_index"]).copy()
    cpi_yoy = _yoy(cpi.set_index("observation_date")["national_cpi_index"]).reset_index()
    cpi_yoy.columns = ["observation_date", "cpi_yoy"]
    cpi_yoy = cpi_yoy.dropna()

    fig2.add_trace(go.Scatter(
        x=rent_yoy["observation_date"], y=rent_yoy["rent_yoy"],
        name="Nashville Rent YoY %", line=dict(color=_ACCENT, width=2),
    ))
    fig2.add_trace(go.Scatter(
        x=cpi_yoy["observation_date"], y=cpi_yoy["cpi_yoy"],
        name="National CPI YoY %", line=dict(color=_AMBER, width=2, dash="dot"),
    ))
    fig2.add_hline(y=0, line_color=_GRID, line_width=1)
    fig2.update_yaxes(title_text="YoY % Change", ticksuffix="%")
    st.plotly_chart(fig2, use_container_width=True)


def page_supply_demand(sdf: pd.DataFrame, year_range: tuple[int, int]) -> None:
    st.header("Supply vs. Demand")
    sf = _date_filter(sdf, year_range)

    col1, col2 = st.columns(2)

    with col1:
        fig = _fig(title="Nashville Metro Permits (Monthly SA)")
        permits = sf.dropna(subset=["metro_permit_count"])
        fig.add_trace(go.Bar(
            x=permits["observation_date"],
            y=permits["metro_permit_count"],
            name="Permits",
            marker_color=_GREEN,
            opacity=0.85,
        ))
        fig.update_yaxes(title_text="Units")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = _fig(title="Davidson County Labor Force")
        labor = sf.dropna(subset=["county_labor_force_count"])
        fig2.add_trace(go.Scatter(
            x=labor["observation_date"],
            y=labor["county_labor_force_count"],
            name="Labor Force",
            line=dict(color=_AMBER, width=2),
            fill="tozeroy",
            fillcolor="rgba(245,166,35,0.07)",
        ))
        fig2.update_yaxes(title_text="Workers", tickformat=",")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    fig3 = _fig(title="3-Month Growth Rates: Rent vs. Labor Force vs. Permits")
    for col, name, color in [
        ("rent_growth_3m_pct", "Rent Growth 3m %", _ACCENT),
        ("labor_force_growth_3m_pct", "Labor Force Growth 3m %", _AMBER),
        ("permit_growth_3m_pct", "Permit Growth 3m %", _GREEN),
    ]:
        valid = sf.dropna(subset=[col])
        fig3.add_trace(go.Scatter(
            x=valid["observation_date"], y=valid[col],
            name=name, line=dict(color=color, width=1.8),
        ))
    fig3.add_hline(y=0, line_color=_GRID, line_width=1)
    fig3.update_yaxes(title_text="% Change (3-month)", ticksuffix="%")
    st.plotly_chart(fig3, use_container_width=True)


def page_affordability(rdf: pd.DataFrame, adf: pd.DataFrame, year_range: tuple[int, int]) -> None:
    st.header("Affordability")

    rf = _date_filter(rdf, year_range)
    af = _date_filter(adf, year_range)

    fig = _fig(title="Rent Burden — Annualized Rent as % of Median Household Income")
    rb = rf.dropna(subset=["rent_burden_pct"])
    fig.add_trace(go.Scatter(
        x=rb["observation_date"], y=rb["rent_burden_pct"],
        name="Rent Burden %",
        line=dict(color=_ACCENT, width=2.5),
        fill="tozeroy",
        fillcolor="rgba(124,106,247,0.08)",
    ))
    fig.add_hline(
        y=30, line_dash="dash", line_color=_RED, line_width=1.5,
        annotation_text="30% threshold", annotation_font_color=_RED,
        annotation_position="top right",
    )
    fig.update_yaxes(title_text="% of Income", ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        fig2 = _fig(title="Composite Affordability Index (0 = affordable, 100 = unaffordable)")
        ai = af.dropna(subset=["affordability_index"])
        fig2.add_trace(go.Scatter(
            x=ai["observation_date"], y=ai["affordability_index"],
            name="Affordability Index",
            line=dict(color=_RED, width=2),
            fill="tozeroy",
            fillcolor="rgba(239,83,80,0.07)",
        ))
        fig2.update_yaxes(title_text="Index Score", range=[0, 100])
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        fig3 = _fig(title="Income Growth vs. CPI Growth (YoY %)")
        ai_valid = af.dropna(subset=["income_growth_yoy_pct", "cpi_yoy_growth_pct"])
        fig3.add_trace(go.Scatter(
            x=ai_valid["observation_date"], y=ai_valid["income_growth_yoy_pct"],
            name="Income Growth YoY", line=dict(color=_GREEN, width=2),
        ))
        fig3.add_trace(go.Scatter(
            x=ai_valid["observation_date"], y=ai_valid["cpi_yoy_growth_pct"],
            name="CPI Growth YoY", line=dict(color=_AMBER, width=2, dash="dot"),
        ))
        fig3.add_hline(y=0, line_color=_GRID, line_width=1)
        fig3.update_yaxes(title_text="YoY % Change", ticksuffix="%")
        st.plotly_chart(fig3, use_container_width=True)


def page_labor(mdf: pd.DataFrame, year_range: tuple[int, int]) -> None:
    st.header("Labor Market — Davidson County")
    mf = _date_filter(mdf, year_range)

    col1, col2 = st.columns(2)

    with col1:
        fig = _fig(title="Unemployment Rate (%)")
        ur = mf.dropna(subset=["county_unemployment_rate"])
        fig.add_trace(go.Scatter(
            x=ur["observation_date"], y=ur["county_unemployment_rate"],
            name="Unemployment Rate",
            line=dict(color=_AMBER, width=2),
            fill="tozeroy",
            fillcolor="rgba(245,166,35,0.07)",
        ))
        fig.update_yaxes(title_text="%", ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = _fig(title="Employment Level")
        emp = mf.dropna(subset=["county_labor_force_count"])
        fig2.add_trace(go.Scatter(
            x=emp["observation_date"], y=emp["county_labor_force_count"],
            name="Labor Force",
            line=dict(color=_GREEN, width=2),
            fill="tozeroy",
            fillcolor="rgba(76,175,135,0.07)",
        ))
        fig2.update_yaxes(title_text="Workers", tickformat=",")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    fig3 = _fig(title="Employment vs. Rent Growth — Does Employment Lead Rent?")
    mf_sorted = mf.sort_values("observation_date")
    labor_yoy = _yoy(mf_sorted.set_index("observation_date")["county_labor_force_count"])
    rent_yoy = _yoy(mf_sorted.set_index("observation_date")["zip_median_asking_rent_usd"])

    labor_yoy = labor_yoy.dropna().reset_index()
    labor_yoy.columns = ["observation_date", "labor_yoy"]
    rent_yoy = rent_yoy.dropna().reset_index()
    rent_yoy.columns = ["observation_date", "rent_yoy"]

    fig3.add_trace(go.Scatter(
        x=labor_yoy["observation_date"], y=labor_yoy["labor_yoy"],
        name="Labor Force Growth YoY %", line=dict(color=_GREEN, width=2),
    ))
    fig3.add_trace(go.Scatter(
        x=rent_yoy["observation_date"], y=rent_yoy["rent_yoy"],
        name="Rent Growth YoY %", line=dict(color=_ACCENT, width=2),
    ))
    fig3.add_hline(y=0, line_color=_GRID, line_width=1)
    fig3.update_yaxes(title_text="YoY % Change", ticksuffix="%")
    st.plotly_chart(fig3, use_container_width=True)


# ── App shell ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nashville Housing Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.title("Nashville Housing Analytics")
    st.caption("Davidson County · 2015–present")
    st.divider()

    page = st.radio(
        "Navigate",
        ["Overview", "Rent Trends", "Supply vs. Demand", "Affordability", "Labor Market"],
        label_visibility="collapsed",
    )

    st.divider()

    min_year, max_year = 2015, pd.Timestamp.now().year
    year_range = st.slider(
        "Year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

    st.caption("Data refreshes every hour. Source: FRED, Zillow ZORI, BLS LAUS, Census ACS, Redfin.")

mdf = load_monthly_metrics()
rdf = load_rent_burden()
sdf = load_supply_demand()
adf = load_affordability()

if page == "Overview":
    page_overview(mdf, rdf, adf, year_range)
elif page == "Rent Trends":
    page_rent_trends(mdf, year_range)
elif page == "Supply vs. Demand":
    page_supply_demand(sdf, year_range)
elif page == "Affordability":
    page_affordability(rdf, adf, year_range)
elif page == "Labor Market":
    page_labor(mdf, year_range)
