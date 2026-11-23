"""Independent Streamlit page: concentration metrics and sensitivity check."""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from concentration_analysis.metrics import SAMPLE_NOTABLE, SAMPLE_FRONTIER

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "concentration_metrics.csv"

st.set_page_config(page_title="Concentration Check | AI Concentration", page_icon="📏", layout="wide")

# Unlike a company count, these measures capture how unevenly model releases
# are distributed across the organisations in each dataset's own sample.
st.title("4. Concentration check: beyond the company count")
st.markdown(
    "**For a competition policy analyst:** do a few companies simply appear in the data, "
    "or are the most visible model releases disproportionately credited to them?"
)
st.markdown(
    "A company count treats a firm with one top-10 model and a firm with six equally. "
    "This page checks the **distribution of model credits** instead."
)

if not DATA_FILE.exists():
    st.error("Concentration data is missing. Run `python -m concentration_analysis.build_metrics` from the repository root.")
    st.stop()

@st.cache_data
def load_metrics():
    return pd.read_csv(DATA_FILE)

metrics = load_metrics()

METRIC = {
    "Effective number of organisations": ("effective_organisations", "Effective organisations (1 / Σp²)", "2f"),
    "Largest organisation's share": ("top_share_pct", "Share of model credits (%)", "1f"),
    "HHI concentration index": ("hhi_0_10000", "HHI (0–10,000)", "0f"),
}

c1, c2 = st.columns([2, 1])
with c1:
    metric_name = st.selectbox("What should concentration mean?", list(METRIC), index=0)
with c2:
    year_range = st.slider("Year range", min_value=int(metrics.year.min()),
                           max_value=int(metrics.year.max()), value=(2023, 2025))
samples = st.multiselect(
    "Compare these samples", [SAMPLE_NOTABLE, SAMPLE_FRONTIER],
    default=[SAMPLE_NOTABLE, SAMPLE_FRONTIER],
    help="Clear both selections to see how the app handles an empty filter.",
)

if not samples:
    st.info("No samples selected. Select at least one dataset to see the concentration chart.")
    st.stop()

filtered = metrics[
    metrics["sample"].isin(samples)
    & metrics["year"].between(year_range[0], year_range[1])
].copy()
if filtered.empty:
    st.info("There are no observations for these filters. Try a later year or select another dataset.")
    st.stop()

measure, y_label, decimals = METRIC[metric_name]
# Unit of the plotted values, named in the legend title
UNIT = {"effective_organisations": "count of organisations", "top_share_pct": "% of model credits",
        "hhi_0_10000": "HHI index points (0 to 10,000)"}
colours = {SAMPLE_NOTABLE: "#2A78D6", SAMPLE_FRONTIER: "#C45F23"}
symbols = {SAMPLE_NOTABLE: "circle", SAMPLE_FRONTIER: "square"}
fig = go.Figure()
for sample in samples:
    rows = filtered[filtered["sample"] == sample].sort_values("year")
    if rows.empty:
        continue
    fmt = ".2f" if decimals == "2f" else (".1f" if decimals == "1f" else ".0f")
    fig.add_trace(go.Scatter(
        x=rows["year"], y=rows[measure], name=sample,
        mode="lines+markers+text",
        text=[format(v, fmt) for v in rows[measure]],
        textposition="top center", textfont=dict(size=12),
        marker=dict(size=11, color=colours[sample], symbol=symbols[sample]),
        line=dict(color=colours[sample], width=3,
                  dash="solid" if sample == SAMPLE_NOTABLE else "dash"),
        hovertemplate="<b>%{fullData.name}</b><br>Year %{x}<br>Value %{y:.2f}<extra></extra>",
    ))
fig.update_layout(
    title=f"{metric_name} by release year and dataset",
    height=450,
    margin=dict(l=12, r=25, t=115, b=20),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=14, color="#3d3d3a"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, title=f"Dataset, {UNIT[measure]}"),
    xaxis=dict(title="Model release year", dtick=1, gridcolor="#eeeeeb"),
    yaxis=dict(title=y_label, rangemode="tozero", gridcolor="#e6e6e3"),
)
st.plotly_chart(fig)

# Keep a complete, qualified statement on screen, independent of hover.
shared_years = sorted(set(metrics[metrics["sample"] == SAMPLE_NOTABLE].year)
                      & set(metrics[metrics["sample"] == SAMPLE_FRONTIER].year)
                      & set(range(year_range[0], year_range[1] + 1)))
if shared_years and len(samples) == 2:
    latest = shared_years[-1]
    a = metrics[(metrics.year == latest) & (metrics["sample"] == SAMPLE_NOTABLE)].iloc[0]
    b = metrics[(metrics.year == latest) & (metrics["sample"] == SAMPLE_FRONTIER)].iloc[0]
    st.markdown(
        f"**What this shows ({latest}).** Among Epoch's notable model releases, the "
        f"effective organisation count is **{a.effective_organisations:.2f}** "
        f"(largest share: **{a.top_share_pct:.1f}%**). "
        f"For the ten highest-ECI models *released that year*, it is "
        f"**{b.effective_organisations:.2f}** (largest share: **{b.top_share_pct:.1f}%**). "
        "The top-10 sample is much smaller by design, so the difference is descriptive, "
        "**not** a direct market-share comparison."
    )
else:
    st.markdown(
        "**How to read the result.** A lower effective organisation count and a higher "
        "HHI or largest-organisation share indicate more concentration **within the chosen sample**."
    )

st.caption(
    "Source: Epoch AI, https://epoch.ai/data (team's raw-data snapshot downloaded "
    "27 Oct 2026). Latest source observations: notable models 12 Oct 2026; "
    "ECI records 15 Oct 2026. **2026 is a partial year**, not directly equivalent to a full year."
)

with st.expander("Check the underlying numbers and methodology"):
    st.dataframe(
        filtered[["year", "sample", "sample_models", "organisations", "top_organisation",
                  "top_share_pct", "hhi_0_10000", "effective_organisations"]]
        .sort_values(["year", "sample"]),
        width="stretch",
    )
    st.markdown(r"""
**Calculation.** For each year, allocate each model one credit. If it has multiple credited
organisations, split that credit equally between them, using the same parent-company
mapping as the group's existing `data_prep.py`. Then calculate each organisation's
share of credits, \(p_i\):

- **HHI** = \(10{,}000\sum_i p_i^2\), using shares from 0 to 1.
- **Effective number of organisations** = \(1/\sum_i p_i^2\).
- **Largest organisation's share** = \(100\max_i p_i\)%.

**Two different samples.** The first is *all Epoch notable model releases in a given year*;
the second is *the ten highest-ECI models among releases in that same year*. These have
different selection criteria and sizes. Comparing their values describes diversity in
those selected datasets; it **does not measure the economy-wide concentration of AI firms**.
In particular, "annual ECI top 10" does not mean the ten strongest models available in
the market at year end. The dataset is curated, performance data are incomplete, and
multiple models from one company count separately.

**Reproduce.** Run `python -m concentration_analysis.build_metrics`. It reads the unchanged
`data/raw/notable_ai_models.csv` and `data/raw/benchmark_data/eci_scores.csv`, and writes
`data/processed/concentration_metrics.csv`. The underlying Epoch files and its licence
are documented in the team's README; verify the applicable licence before publication.
""")
