"""Check a result that could fail if model assignment or formulas change.

Run: python -m concentration_analysis.test_metrics
"""
from .metrics import build_table, SAMPLE_FRONTIER


def main():
    df = build_table()
    eci = df[(df["sample"] == SAMPLE_FRONTIER) & (df["year"] == 2025)].iloc[0]
    assert int(eci["sample_models"]) == 10, "Expected ten ECI models"
    assert int(eci["organisations"]) == 3, "Company count changed"
    assert abs(float(eci["top_share_pct"]) - 60) < 1e-4, "Top share changed"
    assert abs(float(eci["hhi_0_10000"]) - 4400) < 1e-4, "HHI changed"
    assert abs(float(eci["effective_organisations"]) - (1/0.44)) < 1e-4, "Effective N changed"
    assert not df.duplicated(["sample", "year"]).any(), "Duplicate keys"
    print("PASS: 2025 ECI values and all sample/year keys verified.")


if __name__ == "__main__":
    main()
