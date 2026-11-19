# Concentration analysis: metrics and sensitivity check

**Goal:** Extend the existing three-layer narrative without editing `app.py`, `data_prep.py` or any teammate-authored chart.

## What this adds

- A **new Streamlit page**: `pages/4_Concentration_Check.py` (automatically appears in Streamlit's multipage sidebar).
- An additional processing module: `concentration_analysis/metrics.py`.
- A reproducible command: `python -m concentration_analysis.build_metrics`.
- A generated data file: `data/processed/concentration_metrics.csv`.

The page measures distributional concentration, **not just the number of companies**:

- HHI = 10,000 × the sum of squared organisation model-credit shares.
- Effective number of organisations = 1 / sum of squared shares.
- Top organisation's share = the largest model-credit share.

Each jointly credited model gives equal fractional credit to its identified parent companies, using the existing `data_prep.py` entity mapping.

## Integrate (no teammate code changed)

From the team's repository root, copy the new `pages/`, `concentration_analysis/`, and `data/processed/concentration_metrics.csv` paths into the matching locations. Do not replace existing files. Run:

```bash
python -m concentration_analysis.build_metrics
streamlit run app.py
```

The sidebar should then show a separate **Concentration Check** page. `requirements.txt` needs no additions beyond the project's existing Streamlit, pandas and Plotly dependencies.

## User story

**As a** competition policy analyst, **I want** to compare model-credit concentration using several measures and selected periods, **so that** I can distinguish a shrinking list of model publishers from a more uneven distribution of published frontier models.

## Chart choice and alternative

- **Chosen:** labelled multi-series line chart, because the visual task is to compare how concentration changes across years and across two separately defined samples.
- **Rejected:** pie charts for each year, because a sequence of pies makes year-on-year comparison difficult and requires too many panels to see change over time.
- **Two real interactions:** concentration metric selector and year-range slider; a dataset multiselect adds a third, with a deliberately handled empty-selection state.

## Data dictionary: concentration_metrics.csv

| Field | Unit / definition |
|---|---|
| year | Calendar year of the model release (year; 2019–2026 or 2023–2026 depending on sample) |
| sample | Dataset sample, part of composite primary key |
| sample_models | Unique credited model names, model count |
| organisations | Unique parent-normalized organizations receiving model credits, organization count |
| top_organisation | Organization with the greatest share of credits (ties follow pandas ordering) |
| top_share_pct | Maximum organization share of model credits, percent (0–100) |
| hhi_0_10000 | Herfindahl-Hirschman index based on model credits, index points (0–10,000) |
| effective_organisations | Reciprocal of sum of squared fractional model-credit shares, dimensionless effective count |

**Primary key:** (`sample`, `year`). **Source:** Epoch AI [Data](https://epoch.ai/data), files in `data/raw/`:

1. `notable_ai_models.csv` (`Model`, `Organization`, `Publication date`); latest observation 2026-10-12.
2. `benchmark_data/eci_scores.csv` (`Model`, `Organization`, `date`, `eci`); latest observation 2026-10-15.

**Source snapshot:** files already in the team's repository, described by its README as downloaded 2026-10-27. **Licence:** the team's README says Creative Commons Attribution. Check the individual Epoch data/download licences before final submission. **Transforms:** parse dates to release years, select full notable list or ten highest-ECI releases each year, split jointly credited organizations evenly, group known lab aliases by parent company, aggregate annual credits per parent, derive share/HHI/effective number/top share. These operations are implemented in `metrics.py` using existing `data_prep.py` functions. **Refresh:** regenerating from the bundled raw samples does not refresh external data.

**Limits:** HHI of model credits is **not** market concentration by revenue, end-user usage, valuation, capability stock or compute ownership. Comparing all notable releases with a fixed top-ten sample is descriptive because sample sizes differ. 2026 covers only partial-year observations. Source selection and missing benchmarking can bias the values.

## Verify

```bash
python -m concentration_analysis.build_metrics
python -m concentration_analysis.test_metrics
python -m compileall concentration_analysis pages
```

Check 2025 independently: the annual ECI top-ten sample assigns 6/10 models to OpenAI, 2/10 to Google and 2/10 to Anthropic. Hence top share = 60%; HHI = 4400; effective organizations = 1 / 0.44 ≈ 2.27.

## AI assistance notes — record actual use and verification

If you used AI assistance, record what tool you used and which artifact was affected. For this draft, ChatGPT generated suggested code and documentation; do **not** claim you manually authored or checked code you did not personally verify. Before submitting the group AI provenance matrix, run the reproduction command yourself, check 2025 calculations and test the interactive page. Then record those *actual* checks, any corrections and the final outcome in your own row. Do not invent a verification step or a group member's participation.
