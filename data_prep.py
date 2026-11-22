"""Turn the raw Epoch AI files into the processed tables the app reads.

Run from the repository root:  python data_prep.py

The app (app.py) only reads data/processed/. Every table there is written
by this file from the unchanged files in data/raw/, so deleting
data/processed/ and running this file gives back the same tables.
data/DATA_DICTIONARY.md describes every file and column.

The app has three layers, each narrower than the last:
1. Who builds notable models?        data/raw/notable_ai_models.csv
2. Who builds the top-scoring ones?  data/raw/benchmark_data/eci_scores.csv
3. Who owns and uses the AI chips?   data/raw/ai_chip_owners/, data/raw/ai_chip_users/
"""

from pathlib import Path

import pandas as pd

RAW = Path(__file__).parent / "data" / "raw"
OUT = Path(__file__).parent / "data" / "processed"

DOWNLOADED = "2026-10-27"
FIRST_YEAR = 2019
# Epoch's files run to mid-October 2026, so 2026 is a partial year
PARTIAL_YEAR = 2026
CHATGPT_LAUNCH = "2022-11-30"
OTHER = "Other"
NOT_STATED = "Not stated in source"
TOP_N = [10, 20]

# Labs and units that belong to the same company are counted as one organisation
PARENT = {
    "Google": "Google",
    "Google AI": "Google",
    "Google Brain": "Google",
    "Google Cloud": "Google",
    "Google DeepMind": "Google",
    "Google Research": "Google",
    "DeepMind": "Google",
    "Meta AI": "Meta",
    "Facebook": "Meta",
    "Facebook AI": "Meta",
    "Facebook AI Research": "Meta",
    "Meta Superintelligence Labs": "Meta",
    "Microsoft Research": "Microsoft",
    "Microsoft Research Asia": "Microsoft",
    "Alibaba DAMO Academy": "Alibaba",
    "Huawei Noah's Ark Lab": "Huawei",
    "Samsung R&D Institute Russia": "Samsung",
    "Cohere Labs (formerly Cohere for AI)": "Cohere",
    # Epoch's chip-users file names xAI after its merger with SpaceX
    "SpaceXAI": "xAI",
}

# The five organisations with the most notable models from 2019 onwards
NAMED_BUILDERS = ["Google", "OpenAI", "Meta", "Alibaba", "Anthropic"]
# The companies that fill most of the benchmark top 10
NAMED_LEADERS = ["Google", "OpenAI", "Anthropic"]
# The four companies that own the most AI chips
NAMED_OWNERS = ["Google", "Microsoft", "Amazon", "Meta"]


def split_orgs(df: pd.DataFrame, org_col: str) -> pd.DataFrame:
    """One row per (model, organisation), with the model shared out evenly.

    A model built by n organisations gives each of them 1/n of the model,
    so shares in a year add up to 100%.
    """
    rows = df.copy()
    rows["org"] = rows[org_col].str.split(",")
    rows = rows.explode("org")
    rows["org"] = rows["org"].str.strip().replace(PARENT)
    # Two labs of one company on the same model count once
    rows = rows.drop_duplicates(subset=["Model", "org"])
    rows["model_credit"] = 1 / rows.groupby("Model")["org"].transform("count")
    return rows


def named(orgs: pd.Series, keep: list) -> pd.Series:
    return orgs.where(orgs.isin(keep), OTHER)


# Layer 1: who builds notable models

def load_notable() -> pd.DataFrame:
    df = pd.read_csv(RAW / "notable_ai_models.csv")
    df["year"] = pd.to_datetime(df["Publication date"]).dt.year
    return df[df["year"] >= FIRST_YEAR].dropna(subset=["Organization"])


def builders_by_year(notable: pd.DataFrame) -> pd.DataFrame:
    """Each named organisation's share of a year's notable models."""
    rows = split_orgs(notable, "Organization")
    rows["company"] = named(rows["org"], NAMED_BUILDERS)
    out = rows.groupby(["year", "company"])["model_credit"].sum().rename("models").reset_index()
    out["share_pct"] = out["models"] / out.groupby("year")["models"].transform("sum") * 100
    orgs = rows.groupby("year")["org"].nunique().rename("organisations_in_year")
    return out.merge(orgs, on="year")


# Layer 2: who builds the top-scoring models

def load_eci() -> pd.DataFrame:
    df = pd.read_csv(RAW / "benchmark_data" / "eci_scores.csv")
    df["year"] = pd.to_datetime(df["date"]).dt.year
    return df


def eci_top(eci: pd.DataFrame, year: int, n: int) -> pd.DataFrame:
    """The n models of a year with the highest Epoch Capabilities Index.

    A few models have no organisation in Epoch's file (PaLM 2 among them).
    They keep their place in the ranking under NOT_STATED rather than being
    assigned to a company the source does not name.
    """
    top = eci[eci["year"] == year].nlargest(n, "eci")
    top = top[["Model", "Organization", "date", "eci"]].reset_index(drop=True)
    top["Organization"] = top["Organization"].fillna(NOT_STATED)
    top.index += 1
    top["Company"] = top["Organization"].str.split(",").apply(
        lambda orgs: ", ".join(dict.fromkeys(PARENT.get(o.strip(), o.strip()) for o in orgs))
    )
    return top


def eci_top10(eci: pd.DataFrame, year: int) -> pd.DataFrame:
    return eci_top(eci, year, 10)


def eci_top_models(eci: pd.DataFrame) -> pd.DataFrame:
    """Every year's top models by ECI, ranked, down to the largest top N."""
    out = []
    for year in sorted(eci["year"].unique()):
        top = eci_top(eci, year, max(TOP_N)).rename_axis("rank").reset_index()
        top.insert(0, "year", year)
        out.append(top)
    return pd.concat(out, ignore_index=True)


def leaders_by_year(eci: pd.DataFrame) -> pd.DataFrame:
    """Places each company holds in its year's top N, and how many companies share them."""
    out = []
    for n in TOP_N:
        for year in sorted(eci["year"].unique()):
            top = split_orgs(eci_top(eci, year, n), "Organization")
            companies = top.loc[top["org"] != NOT_STATED, "org"].nunique()
            top["company"] = named(top["org"], NAMED_LEADERS)
            for company, places in top.groupby("company")["model_credit"].sum().items():
                out.append({"top_n": n, "year": year, "company": company, "places": places,
                            "companies_in_top": companies})
    return pd.DataFrame(out)


# Layer 3: who owns and uses the chips

def chips_owned() -> pd.DataFrame:
    """AI chips owned at the end of each quarter, in H100-equivalents.

    Epoch splits each owner's stock by chip designer (Nvidia, Google TPU,
    Amazon Trainium...); this adds the designers up. Quarters Epoch marks
    as incomplete are left out.
    """
    df = pd.read_csv(RAW / "ai_chip_owners" / "cumulative_by_designer.csv")
    df = df[df["Incomplete"].isna()]
    df["owner"] = df["Owner"].replace(PARENT)
    df["company"] = named(df["owner"], NAMED_OWNERS)
    out = (df.groupby(["End date", "company"])["Compute estimate in H100e (median)"]
           .sum().rename("h100e").reset_index().rename(columns={"End date": "date"}))
    out["share_pct"] = out["h100e"] / out.groupby("date")["h100e"].transform("sum") * 100
    return out


def chips_used() -> pd.DataFrame:
    """Compute each frontier lab could use at year end (owned or rented)."""
    df = pd.read_csv(RAW / "ai_chip_users" / "year_end_by_lab.csv")
    df["company"] = df["Lab"].replace(PARENT)
    return df[["company", "Lab", "Year", "h100e_p5", "h100e_med", "h100e_p95"]]


# Facts about the whole package, shown on the app's opening screen

def summary(notable: pd.DataFrame, eci: pd.DataFrame, owned: pd.DataFrame) -> pd.DataFrame:
    raw_notable = pd.read_csv(RAW / "notable_ai_models.csv")
    google_2025 = split_orgs(notable[notable["year"] == PARTIAL_YEAR - 1], "Organization")
    google_2025 = google_2025[google_2025["org"] == "Google"]
    rows = [
        ("data_downloaded", DOWNLOADED, "date", "Day the Epoch AI files were downloaded"),
        ("notable_latest", raw_notable["Publication date"].max(), "date",
         "Latest publication date in notable_ai_models.csv"),
        ("eci_latest", eci["date"].max(), "date", "Latest release date in eci_scores.csv"),
        ("chips_latest", owned["date"].max(), "date", "Latest complete quarter in the chip owner file"),
        ("notable_models", len(notable), "models",
         f"Notable models published {FIRST_YEAR} to mid-October {PARTIAL_YEAR} with an organisation"),
        ("notable_organisations", split_orgs(notable, "Organization")["org"].nunique(), "organisations",
         f"Different organisations behind those models, {FIRST_YEAR}-{PARTIAL_YEAR}"),
        ("eci_models", len(eci), "models", "Models with an ECI score, released 2023 to mid-October 2026"),
        ("eci_companies", split_orgs(eci.dropna(subset=["Organization"]), "Organization")["org"].nunique(),
         "organisations", "Different organisations behind the models with an ECI score"),
        ("compute_known_pct_2026",
         round(notable.loc[notable["year"] == PARTIAL_YEAR, "Training compute (FLOP)"].notna().mean() * 100, 1),
         "%", f"Share of {PARTIAL_YEAR} notable models with a training compute figure"),
        ("google_models_2025", len(google_2025), "models", "Google notable models published in 2025"),
        ("google_models_with_compute_2025", int(google_2025["Training compute (FLOP)"].notna().sum()),
         "models", "Of those, models with a training compute figure"),
    ]
    return pd.DataFrame(rows, columns=["metric", "value", "unit", "definition"])


def build(out: Path = OUT) -> list:
    """Write every processed table to `out` and return the file names."""
    out.mkdir(exist_ok=True)
    notable, eci, owned = load_notable(), load_eci(), chips_owned()
    tables = {
        "builders_by_year.csv": builders_by_year(notable),
        "leaders_by_year.csv": leaders_by_year(eci),
        "eci_top_models.csv": eci_top_models(eci),
        "chips_owned_by_quarter.csv": owned,
        "chips_used_by_lab.csv": chips_used(),
        "summary.csv": summary(notable, eci, owned),
    }
    for name, table in tables.items():
        table.to_csv(out / name, index=False)
    return list(tables)


if __name__ == "__main__":
    names = build()
    print(f"Wrote {len(names)} tables to {OUT}")
