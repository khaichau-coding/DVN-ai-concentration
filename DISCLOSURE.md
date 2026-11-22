# Data and AI disclosure statement

## Data

- **Sources.** All data come from Epoch AI (<https://epoch.ai/data>): *Notable AI Models*, the
  *Epoch Capabilities Index* from *Capabilities & benchmarking*, *Data on AI chip owners* and
  *AI chip users*. They were downloaded on 27 October 2026 and are published under the Creative
  Commons Attribution 4.0 licence, which allows reuse with credit to Epoch AI.
- **What we did to them.** The source files are kept unchanged in `data/raw/`. Every number in the
  app comes from tables in `data/processed/`, written from those files by `data_prep.py` and
  `concentration_analysis/build_metrics.py`. `data/DATA_DICTIONARY.md` lists every transform.
  We merged labs of the same company (for example DeepMind into Google), split jointly built models
  evenly between their organisations, and left out Epoch's incomplete Q1 2026 chip estimates.
- **No data was generated, estimated or filled in by us or by AI.** Where the source leaves a value
  blank (for example the organisation of PaLM 2, or Gemini's training compute), the app leaves it
  blank and says so.
- **Limits.** Epoch chooses which models are "notable" and which have benchmark scores; chip
  holdings are estimates with wide ranges; 2026 runs only to mid-October. The app's section "What
  this data cannot show" sets these out, including that model, benchmark and chip shares are not
  market shares by revenue or users.

## AI

- **khaichau-coding** used **Claude** (Anthropic, through Claude Code) to write the code for the main
  page (`app.py`, `data_prep.py`), the check script in `checks/`, and drafts of the README, data
  dictionary and this statement. The question, persona, choice of layers, the 2019 start, the
  ChatGPT marker, and the decision to rank by benchmark score and to add chip ownership were the
  member's own decisions.
- **ggrr8** used **ChatGPT** to generate suggested code and documentation for the Concentration
  Check page, as recorded in `concentration_analysis/README.md`.
- AI was not used to create, alter or fill in any data.
- Every substantive AI use, and the check that verified it, is recorded in
  [`AI_PROVENANCE.md`](AI_PROVENANCE.md). The group takes responsibility for every number and claim
  in the app. The headline numbers are recomputed from the source files by
  `checks/check_numbers.py` and by the manual checks in the provenance matrix.
