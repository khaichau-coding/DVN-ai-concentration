# Data dictionary

Every file in `data/`, what it holds and how it was made.

- `data/raw/` holds the source files exactly as downloaded from Epoch AI on **27 October 2026**.
  They are complete files, not samples, and are never edited.
- `data/processed/` holds the tables the app reads. Each one is written from `data/raw/` by a
  script named below. Delete the folder and run the scripts to get identical files back:

  ```bash
  python data_prep.py                              # main page and Frontier Gap page: eight tables
  python -m concentration_analysis.build_metrics   # Concentration Check page
  python checks/check_numbers.py                   # recompute headline numbers, compare
  ```

All four sources are published by Epoch AI under the **Creative Commons Attribution 4.0** licence
(<https://creativecommons.org/licenses/by/4.0/>): free to use and share with credit to Epoch AI.

## Overview

| File | Kind | Rows | Primary key | Time coverage | Latest observation | Read by |
|---|---|---|---|---|---|---|
| `raw/notable_ai_models.csv` | Source | 1,083 | `Model` | 1950-07-02 to 2026-10-12 | 2026-10-12 | `data_prep.py` |
| `raw/benchmark_data/eci_scores.csv` | Source | 270 | `Model` | 2023-02-24 to 2026-10-15 | 2026-10-15 | `data_prep.py` |
| `raw/ai_chip_owners/cumulative_by_designer.csv` | Source | 215 | `Name` (one per `Owner`, `Chip manufacturer`, `End date`) | Q1 2022 to Q1 2026 | 2026-03-31 (marked incomplete); last complete 2025-12-31 | `data_prep.py` |
| `raw/ai_chip_users/year_end_by_lab.csv` | Source | 11 | `Lab`, `Year` | End 2023 to end 2025 | 2025-12-31 | `data_prep.py` |
| `processed/builders_by_year.csv` | Processed | 42 | `year`, `company` | 2019 to 2026 (2026 to mid-October) | 2026-10-12 | App, layer 1 |
| `processed/leaders_by_year.csv` | Processed | 30 | `top_n`, `year`, `company` | 2023 to 2026 (2026 to mid-October) | 2026-10-15 | App, layer 2 |
| `processed/eci_top_models.csv` | Processed | 80 | `year`, `rank` | 2023 to 2026 | 2026-10-15 | App, layer 2 table |
| `processed/chips_owned_by_quarter.csv` | Processed | 80 | `date`, `company` | Q1 2022 to Q4 2025 | 2025-12-31 | App, layer 3 |
| `processed/chips_used_by_lab.csv` | Processed | 11 | `company`, `Year` | End 2023 to end 2025 | 2025-12-31 | App, layer 3 |
| `processed/summary.csv` | Processed | 11 | `metric` | Whole package | 2026-10-15 | App, opening screen and limits |
| `processed/concentration_metrics.csv` | Processed | 12 | `sample`, `year` | 2019 to 2026 | 2026-10-15 | Concentration Check page |
| `processed/eci_frontier_models.csv` | Processed | 499 | `comparison`, `Model` | 2023-02-24 to 2026-10-15 | 2026-10-15 | Frontier Gap page |
| `processed/frontier_gap.csv` | Processed | 16 | `comparison`, `period_end` | Mid-2023 to mid-October 2026 | 2026-10-15 | Frontier Gap page |

---

## Source files

### `raw/notable_ai_models.csv`

- **Source:** Epoch AI, *Notable AI Models*.
- **URL:** <https://epoch.ai/data/notable-ai-models>, file <https://epoch.ai/data/notable_ai_models.csv>
- **Licence:** CC BY 4.0.
- **What a row is:** one AI model that Epoch judges notable (state of the art, highly cited, or
  historically significant). **Primary key:** `Model` (unique in the file).
- **Coverage:** publication dates 1950-07-02 to 2026-10-12. The app uses 2019 onwards.

| Column used | Type and unit | Meaning |
|---|---|---|
| `Model` | text | Model name |
| `Organization` | text, comma-separated list | Organisations that built the model; 18 rows are blank |
| `Publication date` | date (YYYY-MM-DD) | Date the model was published |
| `Training compute (FLOP)` | number, floating-point operations | Compute used to train the model; blank when not disclosed or estimated |

The other 43 columns (parameters, dataset size, hardware, cost, authors and so on) are kept
unchanged and not used.

### `raw/benchmark_data/eci_scores.csv`

- **Source:** Epoch AI, *Capabilities & benchmarking*, Epoch Capabilities Index (ECI).
- **URL:** <https://epoch.ai/benchmarks>, file inside <https://epoch.ai/data/benchmark_data.zip>
  (`epoch_capabilities_index/eci_scores.csv`).
- **Licence:** CC BY 4.0.
- **What a row is:** one model with an ECI score. **Primary key:** `Model` (unique in the file).
- **Coverage:** release dates 2023-02-24 to 2026-10-15.

| Column used | Type and unit | Meaning |
|---|---|---|
| `Model` | text | Model name |
| `eci` | number, ECI index points | Epoch's combined score across many benchmarks; higher is more capable. Range in this file 54.81 to 168.83 |
| `date` | date (YYYY-MM-DD) | Model release date |
| `Organization` | text, comma-separated list | Organisation(s) that built the model; 17 rows are blank, including PaLM 2-L, PaLM 2-M and internlm-20b |

Not used: `Display name`, `eci_ci_low`, `eci_ci_high` (Epoch's uncertainty bounds on the score),
`Country (of organization)`, `Model accessibility`, `Accessibility group`, `model_versions`.

### `raw/ai_chip_owners/cumulative_by_designer.csv`

- **Source:** Epoch AI, *Data on AI chip owners*.
- **URL:** <https://epoch.ai/data/ai-chip-owners>, file inside <https://epoch.ai/data/ai_chip_owners.zip>
- **Licence:** CC BY 4.0.
- **What a row is:** one owner's cumulative stock of AI chips from one chip designer at the end of
  one quarter. **Primary key:** `Name` (unique; equivalent to `Owner` + `Chip manufacturer` + `End date`).
- **Coverage:** quarters ending 2022-03-31 to 2026-03-31. Epoch marks all Q1 2026 rows incomplete.

| Column used | Type and unit | Meaning |
|---|---|---|
| `Owner` | text | Google, Microsoft, Amazon, Meta, Oracle, CoreWeave, xAI, China, China (smuggled), Other |
| `Chip manufacturer` | text | Chip designer: Nvidia, Google, Amazon, AMD, Huawei, Cambricon |
| `End date` | date (YYYY-MM-DD) | Last day of the quarter |
| `Compute estimate in H100e (median)` | number, H100-equivalents | Median estimate of the stock, as a number of Nvidia H100 chips of equal computing power |
| `Incomplete` | `True` or blank | `True` when Epoch's estimate for that quarter is not finished |

Not used: start date, 5th/95th percentile bounds, unit counts, power in MW, notes and edit history.

### `raw/ai_chip_users/year_end_by_lab.csv`

- **Source:** Epoch AI, *AI chip users*.
- **URL:** <https://epoch.ai/data/ai-chip-users>, file inside <https://epoch.ai/data/ai_chip_users.zip>
- **Licence:** CC BY 4.0.
- **What a row is:** the compute one frontier lab could use at the end of one year, whether it owns
  the chips or rents them. **Primary key:** `Lab` + `Year`.
- **Coverage:** end 2023 (OpenAI only), end 2024 and end 2025 (five labs).

| Column used | Type and unit | Meaning |
|---|---|---|
| `Lab` | text | OpenAI, Google DeepMind, Meta Superintelligence Labs, Anthropic, SpaceXAI |
| `Year` | year | Year whose end the estimate describes |
| `h100e_med` | number, H100-equivalents | Median estimate |
| `h100e_p5`, `h100e_p95` | number, H100-equivalents | 5th and 95th percentile of Epoch's estimate |

Not used: `Name`, `Date` (always 31 December of `Year`), `Notes`.

---

## Processed files

Shared steps, all in `data_prep.py`:

- **Company merge (`PARENT`):** Google, Google AI, Google Brain, Google Cloud, Google DeepMind,
  Google Research and DeepMind count as **Google**; Meta AI, Facebook, Facebook AI, Facebook AI
  Research and Meta Superintelligence Labs count as **Meta**; Microsoft Research (and Asia) count as
  **Microsoft**; SpaceXAI counts as **xAI**; and a few smaller merges listed in the code.
- **Splitting joint models (`split_orgs`):** a model with *n* organisations gives each 1/*n* of a
  model. Two labs of one company on the same model count once.

### `processed/builders_by_year.csv`

Layer 1: each named organisation's share of a year's notable models.

| Column | Type and unit | Meaning |
|---|---|---|
| `year` | year | Publication year, 2019 to 2026 |
| `company` | text | Google, OpenAI, Meta, Alibaba, Anthropic (the five with most notable models 2019 to 2026), or Other |
| `models` | number, models (fractional) | Notable models credited to that company that year |
| `share_pct` | number, % | `models` as a share of that year's total; adds to 100 per year |
| `organisations_in_year` | count, organisations | Different organisations with at least part of a notable model that year (same for every row of a year) |

**Transform:** `notable_ai_models.csv` → keep publication year ≥ 2019 and a non-blank
`Organization` (701 models) → split joint models → merge companies → group organisations outside
the five named into Other → sum credits by year and company → divide by the year total.

### `processed/leaders_by_year.csv`

Layer 2: places each company holds in a year's ECI top 10 and top 20.

| Column | Type and unit | Meaning |
|---|---|---|
| `top_n` | count | Size of the ranking: 10 or 20 |
| `year` | year | Release year, 2023 to 2026 |
| `company` | text | Google, OpenAI, Anthropic, or Other |
| `places` | number, models | Places in that year's top `top_n` held by the company |
| `companies_in_top` | count, organisations | Different organisations in that year's top `top_n`, not counting models with no stated organisation |

**Transform:** `eci_scores.csv` → year from `date` → for each year take the `top_n` highest `eci`
→ blank organisations become "Not stated in source" → split joint models → merge companies → count
distinct organisations (excluding "Not stated in source") → group all but Google, OpenAI and
Anthropic into Other → sum places.

### `processed/eci_top_models.csv`

Layer 2 table: the models behind `leaders_by_year.csv`.

| Column | Type and unit | Meaning |
|---|---|---|
| `year` | year | Release year |
| `rank` | integer, 1 = highest | Rank by ECI within the year; the app shows rank ≤ 10 or ≤ 20 |
| `Model`, `Organization`, `date`, `eci` | as in the source | Copied from `eci_scores.csv`; blank `Organization` shown as "Not stated in source" |
| `Company` | text | `Organization` after the company merge |

**Transform:** `eci_scores.csv` → for each year sort by `eci`, keep the top 20, number them.

### `processed/chips_owned_by_quarter.csv`

Layer 3: AI chips owned at each quarter end.

| Column | Type and unit | Meaning |
|---|---|---|
| `date` | date (YYYY-MM-DD) | Quarter end, 2022-03-31 to 2025-12-31 |
| `company` | text | Google, Microsoft, Amazon, Meta, or Other (Oracle, CoreWeave, xAI, China, China (smuggled), Other) |
| `h100e` | number, H100-equivalents | Median estimate of chips owned, summed over chip designers |
| `share_pct` | number, % of H100e | `h100e` as a share of all owners that quarter; adds to 100 per quarter |

**Transform:** `cumulative_by_designer.csv` → drop rows with `Incomplete` = True (all of Q1 2026)
→ group owners outside the four named into Other → sum the median H100e over chip designers
→ divide by the quarter total. The app shows the first quarter and every December.

### `processed/chips_used_by_lab.csv`

Layer 3 dot plot: compute available to each frontier lab.

| Column | Type and unit | Meaning |
|---|---|---|
| `company` | text | `Lab` after the company merge (Google DeepMind → Google, SpaceXAI → xAI, Meta Superintelligence Labs → Meta) |
| `Lab`, `Year` | as in the source | |
| `h100e_p5`, `h100e_med`, `h100e_p95` | number, H100-equivalents | Copied from the source |

**Transform:** `year_end_by_lab.csv` → rename labs to companies; values unchanged. The app shows 2024 and 2025.

### `processed/summary.csv`

Facts about the whole package, shown on the opening screen and in "What this data cannot show".

| Column | Type and unit | Meaning |
|---|---|---|
| `metric` | text | Name of the fact (primary key) |
| `value` | text or number | The value; dates as YYYY-MM-DD |
| `unit` | text | Unit of `value` |
| `definition` | text | What the value counts and over which period |

**Transform:** counts and dates computed in `summary()` in `data_prep.py` from the same filtered
tables as above (for example, 15 Google notable models in 2025, of which 1 has a compute figure).

### `processed/concentration_metrics.csv`

Concentration Check page. Written by `python -m concentration_analysis.build_metrics`; documented
in full in `concentration_analysis/README.md`. Columns: `year`, `sample`, `sample_models`,
`organisations`, `top_organisation`, `top_share_pct` (%), `hhi_0_10000` (HHI index points,
0 to 10,000), `effective_organisations` (dimensionless count). **Primary key:** `sample` + `year`.
**Transform:** notable models per year, or each year's ECI top 10 → split joint models → merge
companies → shares of model credits → HHI = 10,000 × Σ share², effective number = 1 / Σ share².

### `processed/eci_frontier_models.csv`

Frontier Gap page: every ECI model placed in a leading or a chasing group, with its group's best
score so far.

| Column | Type and unit | Meaning |
|---|---|---|
| `comparison` | text | "Top 3 vs every other company" or "Closed weights vs open weights" |
| `group` | text | Top 3: OpenAI, Google, Anthropic / Every other company; or Closed weights / Open weights |
| `role` | text | `leading` or `chasing` |
| `Model`, `Organization`, `date`, `eci` | as in the source | Copied from `eci_scores.csv` |
| `best_so_far` | number, ECI index points | Highest `eci` in the same group released on or before `date` |
| `is_record` | `True` / `False` | `True` when the model raised its group's best score |

**Transform:** `eci_scores.csv` → Top 3 comparison: drop the 17 models with no organisation, then
a model is in the Top 3 group if any of its organisations (after the company merge) is OpenAI,
Google or Anthropic (253 models). Weights comparison: keep `Accessibility group` Closed weights or
Open weights, dropping the 24 "Other" models of unknown or limited access (246 models) → sort by
date → running maximum of `eci` within each group.

### `processed/frontier_gap.csv`

Frontier Gap page: the gap between the two groups at each half-year end and at the latest date.

| Column | Type and unit | Meaning |
|---|---|---|
| `comparison` | text | As above |
| `period_end` | date (YYYY-MM-DD) | 30 June or 31 December from 2023-06-30, then the latest model date, 2026-10-15 |
| `leading_best_eci`, `chasing_best_eci` | number, ECI index points | Each group's best score released on or before `period_end` |
| `leading_best_model`, `chasing_best_model` | text | The models with those scores |
| `chasing_best_date` | date | Release date of `chasing_best_model` |
| `gap_eci` | number, ECI index points | `leading_best_eci` minus `chasing_best_eci` |
| `leading_first_reached_model`, `leading_first_reached_date` | text, date | First leading-group model with an ECI at least `chasing_best_eci` |
| `months_behind` | number, months (days / 30.44) | `chasing_best_date` minus `leading_first_reached_date`; blank when not positive (mid-2023, before the leading group's first scored model) |

**Transform:** `eci_frontier_models.csv` → for each comparison and period end, take each group's
highest `eci` so far, subtract, and find the earliest leading model at or above the chasing best.
