"""Turn the raw Epoch AI files into the tables the app shows.

Every number in the app comes from the files in data/raw/ through the
functions below. Running this file writes the same tables to
data/processed/ so they can be opened and checked in Excel.

The app has three layers, each narrower than the last:
1. Who builds notable models?        data/raw/notable_ai_models.csv
2. Who builds the most capable ones? data/raw/benchmark_data/eci_scores.csv
3. Who owns and uses the AI chips?   data/raw/ai_chip_owners/, data/raw/ai_chip_users/
"""

from pathlib import Path

import pandas as pd

RAW = Path(__file__).parent / "data" / "raw"
OUT = Path(__file__).parent / "data" / "processed"

FIRST_YEAR = 2019
# Epoch's files run to mid-October 2026, so 2026 is a partial year
PARTIAL_YEAR = 2026
CHATGPT_LAUNCH = "2022-11-30"
OTHER = "Other"

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
    out["share"] = out["models"] / out.groupby("year")["models"].transform("sum") * 100
    return out


def builders_count(notable: pd.DataFrame, year: int) -> int:
    """How many different organisations published a notable model that year."""
    return split_orgs(notable[notable["year"] == year], "Organization")["org"].nunique()


# Layer 2: who builds the most capable models

def load_eci() -> pd.DataFrame:
    df = pd.read_csv(RAW / "benchmark_data" / "eci_scores.csv")
    df["year"] = pd.to_datetime(df["date"]).dt.year
    return df


def eci_top10(eci: pd.DataFrame, year: int) -> pd.DataFrame:
    """The ten models of a year with the highest Epoch Capabilities Index."""
    top = eci[eci["year"] == year].nlargest(10, "eci")
    top = top[["Model", "Organization", "date", "eci"]].reset_index(drop=True)
    top.index += 1
    top["Company"] = top["Organization"].str.split(",").apply(
        lambda orgs: ", ".join(dict.fromkeys(PARENT.get(o.strip(), o.strip()) for o in orgs))
    )
    return top


def leaders_by_year(eci: pd.DataFrame) -> pd.DataFrame:
    """Slots each company holds in its year's top 10, and how many companies share them."""
    out = []
    for year in sorted(eci["year"].unique()):
        top = split_orgs(eci_top10(eci, year), "Organization")
        companies = top["org"].nunique()
        top["company"] = named(top["org"], NAMED_LEADERS)
        slots = top.groupby("company")["model_credit"].sum()
        for company, n in slots.items():
            out.append({"year": year, "company": company, "slots": n, "companies_in_top10": companies})
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
           .sum().rename("h100e").reset_index())
    out["date"] = pd.to_datetime(out["End date"])
    out["share"] = out["h100e"] / out.groupby("date")["h100e"].transform("sum") * 100
    return out.drop(columns="End date")


def chips_used() -> pd.DataFrame:
    """Compute each frontier lab could use at year end (owned or rented)."""
    df = pd.read_csv(RAW / "ai_chip_users" / "year_end_by_lab.csv")
    df["company"] = df["Lab"].replace(PARENT)
    return df[["company", "Lab", "Year", "h100e_p5", "h100e_med", "h100e_p95"]]


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.csv"):
        old.unlink()
    notable, eci = load_notable(), load_eci()
    builders_by_year(notable).to_csv(OUT / "builders_by_year.csv", index=False)
    leaders_by_year(eci).to_csv(OUT / "leaders_by_year.csv", index=False)
    for year in sorted(eci["year"].unique()):
        eci_top10(eci, year).to_csv(OUT / f"eci_top10_{year}.csv", index_label="Rank")
    chips_owned().to_csv(OUT / "chips_owned_by_quarter.csv", index=False)
    chips_used().to_csv(OUT / "chips_used_by_lab.csv", index=False)
    print(f"Wrote tables to {OUT}")
