"""Recompute the app's headline numbers straight from data/raw/ and compare.

Run from the repository root:  python checks/check_numbers.py

Checks 1 to 4 deliberately do not use data_prep.py: each one redoes
the calculation in a few lines of plain pandas, so a bug in data_prep.py
(a wrong filter, a broken company merge, a dropped quarter) makes it fail.
It also rebuilds every processed table and checks it matches the
committed file. Exits with status 1 if any check fails.
"""

import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
GOOGLE = r"Google|DeepMind"

results = []


def check(name, expected, actual):
    ok = expected == actual if not isinstance(expected, float) else abs(expected - actual) < 0.05
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: processed={expected} recomputed={actual}")


summary = pd.read_csv(PROCESSED / "summary.csv").set_index("metric")["value"]

# 1. Companies holding the 2025 ECI top 10 (the number traced in the video)
eci = pd.read_csv(RAW / "benchmark_data" / "eci_scores.csv")
top = eci[eci["date"].str.startswith("2025")].nlargest(10, "eci")
companies = top["Organization"].str.replace(GOOGLE, "Google", regex=True).str.split(",").explode()
leaders = pd.read_csv(PROCESSED / "leaders_by_year.csv")
check("Companies in the 2025 ECI top 10",
      int(leaders.query("top_n == 10 and year == 2025")["companies_in_top"].iloc[0]),
      companies.str.strip().nunique())

# 2. Layer 1 shares add up to 100% in every year
builders = pd.read_csv(PROCESSED / "builders_by_year.csv")
sums = builders.groupby("year")["share_pct"].sum()
check("Years whose layer 1 shares add to 100%", len(sums), int(((sums - 100).abs() < 1e-6).sum()))

# 3. Google's 2025 notable models and how many report training compute
notable = pd.read_csv(RAW / "notable_ai_models.csv")
google = notable[notable["Publication date"].str.startswith("2025")
                 & notable["Organization"].str.contains(GOOGLE, na=False)]
check("Google notable models in 2025", int(summary["google_models_2025"]), len(google))
check("Of those, with a compute figure", int(summary["google_models_with_compute_2025"]),
      int(google["Training compute (FLOP)"].notna().sum()))

# 4. Share of AI chips owned by Google, Microsoft, Amazon and Meta at the end of 2025
owners = pd.read_csv(RAW / "ai_chip_owners" / "cumulative_by_designer.csv")
end = owners[(owners["End date"] == "2025-12-31") & owners["Incomplete"].isna()]
h100e = end.groupby("Owner")["Compute estimate in H100e (median)"].sum()
recomputed = h100e[["Google", "Microsoft", "Amazon", "Meta"]].sum() / h100e.sum() * 100
owned = pd.read_csv(PROCESSED / "chips_owned_by_quarter.csv")
latest = owned[(owned["date"] == "2025-12-31") & (owned["company"] != "Other")]
check("Top-4 share of AI chips, end 2025 (%)", round(latest["share_pct"].sum(), 2), round(recomputed, 2))

# 5. Frontier gap page: latest gap between the top 3 and every other named company
named_eci = eci.dropna(subset=["Organization"])
is_top3 = named_eci["Organization"].str.contains("OpenAI|Anthropic|" + GOOGLE)
gap = pd.read_csv(PROCESSED / "frontier_gap.csv")
latest_gap = gap[gap["comparison"] == "Top 3 vs every other company"].iloc[-1]
check("Latest top 3 gap (ECI points)", float(latest_gap["gap_eci"]),
      round(named_eci.loc[is_top3, "eci"].max() - named_eci.loc[~is_top3, "eci"].max(), 2))

# 6. Every processed table regenerates byte for byte from data/raw/
sys.path.insert(0, str(ROOT))
import data_prep  # noqa: E402  (only used to rebuild, never to compute the checks above)

with tempfile.TemporaryDirectory() as tmp:
    for name in data_prep.build(Path(tmp)):
        check(f"{name} regenerates unchanged", True,
              (Path(tmp) / name).read_bytes() == (PROCESSED / name).read_bytes())

print(f"\n{sum(results)} of {len(results)} checks passed.")
sys.exit(0 if all(results) else 1)
