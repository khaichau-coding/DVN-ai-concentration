"""Run from the repository root: python -m concentration_analysis.build_metrics"""
from pathlib import Path
from .metrics import build_table


def main():
    project_root = Path(__file__).resolve().parents[1]
    output = project_root / "data" / "processed" / "concentration_metrics.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    table = build_table()
    table.to_csv(output, index=False)
    print(f"Wrote {len(table)} rows to {output}")
    print(table[table["year"] == 2025].to_string(index=False))


if __name__ == "__main__":
    main()
