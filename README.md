# Is frontier AI capability concentrating in fewer organisations?

An interactive data narrative built with Streamlit for Assignment 3, *The Rise of
Artificial Intelligence: Data Narrative Studio*.

**Persona.** A competition policy analyst deciding whether AI is becoming a market that a
handful of firms control.

**Answer in one line.** It depends on the layer: many organisations publish notable models,
only three companies build the most capable ones, and four companies own most of the chips.

## Data

All from Epoch AI (<https://epoch.ai/data>), downloaded on 27 October 2026, Creative Commons
Attribution licence. The files are kept unchanged in `data/raw/`.

| Layer | File | Epoch dataset |
|---|---|---|
| 1. Who builds notable models | `notable_ai_models.csv` | Notable AI Models |
| 2. Who builds the most capable models | `benchmark_data/eci_scores.csv` | Capabilities & benchmarking (Epoch Capabilities Index) |
| 3. Who owns the chips | `ai_chip_owners/cumulative_by_designer.csv` | AI chip owners |
| 3. Who can use the chips | `ai_chip_users/year_end_by_lab.csv` | AI chip users |

## How the numbers are made

All processing is in `data_prep.py`:

1. Split the organisation column on commas, so a joint model gives one row per organisation,
   and split the model evenly between them.
2. Merge labs of the same company (for example Google Brain and DeepMind count as Google).
3. Layer 1: each organisation's share of the year's notable models, from 2019.
4. Layer 2: each year's ten highest ECI scores and the companies behind them, from 2023.
5. Layer 3: each owner's AI chips at the end of each quarter, in H100-equivalents, from 2022.

Run `python data_prep.py` to write every table the app shows to `data/processed/`.

## Project structure

```
app.py               Streamlit app: the three layers and their charts
data_prep.py         Every calculation, from raw files to the tables the app shows
data/raw/            Epoch AI files, unchanged
data/processed/      Tables written by data_prep.py, for checking numbers in Excel
requirements.txt     Pinned package versions
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
