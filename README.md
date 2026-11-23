# Is frontier AI capability concentrating in fewer organisations?

An interactive data narrative built with Streamlit for Assignment 3, *The Rise of Artificial
Intelligence: Data Narrative Studio*.

- **Live app:** https://dvn-ai-concentration.streamlit.app
- **Repository:** <https://github.com/khaichau-coding/DVN-ai-concentration>
- **Assessed version:** _add the release tag or commit hash here_

## Question

**Is frontier AI capability concentrating in fewer organisations?**

## Persona and decision

**A competition policy analyst** at a competition authority, who has to decide whether AI is
becoming a market that a handful of firms control, and so whether it needs closer competition
scrutiny (a market study, merger review attention, or access-to-compute remedies).

## Answer, and why it is arguable

**Yes at the frontier, not across the whole field.** In 2025 the ten highest-scoring models by
the Epoch Capabilities Index came from 3 companies, down from 6 in 2023 (top 20: 10 down to 6), and
four companies owned 63% of the world's AI chips. But 43 organisations published a notable model in
2025, and organisations outside the five largest made 46% of them.

The same data supports a different answer: an analyst who counts who *publishes* models sees an
open, even widening field (outside organisations reached 65% of notable models in 2024). The app
shows both readings and argues the frontier and the chips matter more for competition.

## User stories

1. **As a** competition policy analyst, **I want** to see how the share of notable models held by the
   largest developers changed before and after ChatGPT's launch, **so that** I can judge whether AI
   development as a whole is opening up or closing in.
   *Walk-through:* opening screen, first metric (701 models from 254 organisations) → section 1
   chart, reading the bars either side of the ChatGPT line → the table under it for exact shares
   and the number of organisations publishing each year.

2. **As a** competition policy analyst, **I want** to see which companies hold the top of the
   benchmark ranking each year, for both the top 10 and the top 20, **so that** I can tell whether
   frontier capability is concentrated and not just publishing activity.
   *Walk-through:* section 2 → read the company count above each bar → switch **Top 10 / Top 20**
   to check the pattern holds → move the year slider to see exactly which models hold the places.

3. **As a** competition policy analyst, **I want** to see who owns the AI chips and how much compute
   each frontier lab can use, **so that** I can judge whether access to compute is controlled by a
   few firms that the model leaders depend on.
   *Walk-through:* section 3 chip-ownership chart, comparing the first bar (before ChatGPT) with end
   2025 → the lab compute dot plot and its table of estimate ranges → "What this data cannot show".

The **Frontier Gap** page (sidebar) tests the answer from the other side. Since the end of 2024
the best model from outside OpenAI, Google and Anthropic has trailed by 6.2 to 10.1 ECI points and
3 to 6 months, without a steady widening, which supports reading the frontier as crowded rather
than locked up. The gap to the best open-weights model has grown, from 6.2 points in mid-2025 to
about 11, which supports the opposite reading.

The **Concentration Check** page (sidebar) adds a fourth story by ggrr8: comparing concentration with
HHI, the effective number of organisations and the largest share. See
`concentration_analysis/README.md`.

## What is in the app

| Chart | Visual task | Form | Visual Vocabulary family | Interaction |
|---|---|---|---|---|
| 1. Share of notable models by organisation, 2019 to 2026 | How the whole splits between organisations, year by year | 100% stacked column, ChatGPT marker | Part-to-whole | Hover; full values in the table |
| 2. Places in the ECI top 10 or 20 by company, 2023 to 2026 | How many places each company holds, and how many companies share them | Stacked column of counts | Part-to-whole | **Top 10 / Top 20 toggle**, **year slider** for the model table |
| 3. Share of AI chips owned, March 2022 to December 2025 | Who owns what share of all AI chips | 100% stacked column with totals | Part-to-whole | Hover |
| 4. Compute each lab can use, end 2024 and end 2025 | Rank labs and show how uncertain the estimates are | Ordered dot plot with 5th to 95th percentile ranges | Ranking | Hover; ranges in the table |
| 5. Concentration Check (separate page) | How concentration measures change over time | Labelled line chart | Change over time | Metric selector, year range, sample filter with an empty-selection message |
| 6. Frontier Gap (separate page) | How far the best models outside the leading group trail it, and whether the gap widens | Step lines of the best score so far over a dot strip of every model, gap labelled | Change over time | Comparison toggle (top 3 vs others, closed vs open weights), year range |

**Readability.** Every chart has a title stating what it shows, and labelled axes and legends with
units. Values are written on the bars and dots; small segments and uncertainty ranges are in a
table under the chart, so nothing needs hovering. Sources and the data refresh date are at the
top and bottom of the page.

**Colour.** Each company keeps one colour across all charts. Each chart's set of colours, including
the Concentration Check page, was checked with a colour-vision-deficiency validator (OKLab colour
distance under simulated protan, deutan and tritan vision, plus a normal-vision floor). Every set
passed; the closest pair (Microsoft green and Amazon red in chart 3) sits at the floor, so those
segments also carry written values and names. Results: [`checks/colour_check.md`](checks/colour_check.md).

**Speed.** The main page reads only small CSV files from `data/processed/`. Layer 2 is a Streamlit
fragment, so its toggle and slider redraw only that section (about 0.9 seconds locally).

## Data

All data are from Epoch AI (<https://epoch.ai/data>), downloaded on 27 October 2026, Creative
Commons Attribution 4.0. `data/DATA_DICTIONARY.md` documents every file: source, URL, licence,
columns and units, primary key, time coverage, latest observation and the transform that made it.

```
data/raw/          Four Epoch AI files, unchanged
data/processed/    Nine tables the app reads, written by the scripts below
data/DATA_DICTIONARY.md
```

## Reproduce

```bash
pip install -r requirements.txt
python data_prep.py                              # rebuild the main and Frontier Gap tables
python -m concentration_analysis.build_metrics   # rebuild the Concentration Check table
python checks/check_numbers.py                   # recompute headline numbers from raw, compare
python -m concentration_analysis.test_metrics    # check the Concentration Check values
streamlit run app.py
```

`checks/check_numbers.py` redoes the headline numbers in plain pandas without `data_prep.py`, and
rebuilds every processed table to confirm it matches the committed file byte for byte.

## Project structure

```
app.py                         Main page: question, answer, three layers, limits
pages/4_Concentration_Check.py Concentration Check page (ggrr8)
pages/5_Frontier_Gap.py        Frontier Gap page: how far the others trail the leading group
data_prep.py                   Every calculation for the main page, raw to processed
concentration_analysis/        Calculations and test for the Concentration Check page (ggrr8)
checks/check_numbers.py        Independent recomputation of headline numbers
data/                          Raw files, processed files, data dictionary
AI_PROVENANCE.md               AI provenance matrix, one row per substantive AI use
DISCLOSURE.md                  Data and AI disclosure statement
requirements.txt               Pinned package versions
```

## Team

|Team Member | GitHub account | Contribution |
|---|---|---|
| Minh Khai Chau| khaichau-coding | Question, persona, layers 1 to 3 of the main page, data package, checks |
| Gorui Gao| ggrr8 | Concentration Check page and `concentration_analysis/` |
| Arhan Ali Syed | Arhan789 | Frontier_Gap page |

## Data and AI disclosure

See [`DISCLOSURE.md`](DISCLOSURE.md) and the provenance matrix in [`AI_PROVENANCE.md`](AI_PROVENANCE.md).
