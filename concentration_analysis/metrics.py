"""Reproducible measures of model-publisher concentration.

Sources: existing Epoch AI raw samples and entity resolution from data_prep.py.
No code or data from other contributors is overwritten.
"""
from __future__ import annotations

import pandas as pd

from data_prep import eci_top10, load_eci, load_notable, split_orgs


SAMPLE_NOTABLE = "All notable model releases"
SAMPLE_FRONTIER = "Annual ECI top 10"


def summarize_credits(year: int, sample: str, sample_models: pd.DataFrame,
                      source_column: str = "Organization") -> dict:
    """Calculate concentration after assigning equal credit to co-developers.

    HHI = 10,000 * sum(p_i ** 2); effective_n = 1 / sum(p_i ** 2),
    where p_i is the organisation's share of model credits in the sample.
    """
    credits = (split_orgs(sample_models, source_column)
               .groupby("org", as_index=True)["model_credit"].sum())
    if credits.empty or credits.sum() <= 0:
        raise ValueError(f"No model credits for {sample} in {year}")
    p = credits / credits.sum()
    top = credits.idxmax()
    concentration = float((p ** 2).sum())
    return {
        "year": int(year),
        "sample": sample,
        "sample_models": int(sample_models["Model"].nunique()),
        "organisations": int(p.size),
        "top_organisation": str(top),
        "top_share_pct": round(float(p.max() * 100), 6),
        "hhi_0_10000": round(concentration * 10_000, 6),
        "effective_organisations": round(1 / concentration, 6),
    }


def build_table() -> pd.DataFrame:
    """Generate annual metrics from source samples, not grouped 'Other' data."""
    notable = load_notable()
    benchmark = load_eci()
    out = []
    for year, subset in notable.groupby("year", sort=True):
        out.append(summarize_credits(int(year), SAMPLE_NOTABLE, subset))
    for year in sorted(benchmark["year"].unique()):
        subset = eci_top10(benchmark, int(year))
        out.append(summarize_credits(int(year), SAMPLE_FRONTIER, subset))
    df = pd.DataFrame(out).sort_values(["sample", "year"]).reset_index(drop=True)
    if df.duplicated(["sample", "year"]).any():
        raise AssertionError("Duplicate sample/year records")
    if not df["effective_organisations"].between(1, df["organisations"] + 1e-6).all():
        raise AssertionError("Invalid effective organisation counts")
    if not df["top_share_pct"].between(0, 100).all():
        raise AssertionError("Invalid top shares")
    return df
