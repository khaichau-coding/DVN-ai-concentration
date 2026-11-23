# Colour vision deficiency check

Each chart's colours were run through a palette validator that converts them to OKLab and measures
the colour distance (ΔE × 100) between pairs under simulated protanopia, deuteranopia and
tritanopia, plus normal vision. Targets: CVD ΔE ≥ 8 (6 to 8 is a floor allowed only when another
cue, such as a written label, also identifies the series); normal-vision ΔE ≥ 15. "Adjacent" checks
segments that touch in a stack; "all" checks every pair. Run on 22 November 2026, light mode,
surface `#fcfcfb`.

| Chart | Colours | Pairs | Worst CVD ΔE | Worst normal ΔE | Result |
|---|---|---|---|---|---|
| 1. Notable models | Google `#2a78d6`, OpenAI `#eb6834`, Anthropic `#1baf7a`, Meta `#eda100`, Alibaba `#e87ba4` | adjacent | 9.1 (Meta/Anthropic, protan) | 19.6 | Pass |
| 2. ECI top 10/20 | Google, OpenAI, Anthropic | all | 9.2 (Anthropic/OpenAI, deutan) | 24.0 | Pass |
| 3. AI chips owned | Google `#2a78d6`, Microsoft `#008300`, Amazon `#e34948`, Meta `#eda100` | all | 7.2 (Amazon/Microsoft, protan) | 20.8 | Pass at floor: every segment also carries its value, and the last bar its owner's name |
| 5. Concentration Check | `#2A78D6`, `#C45F23` | all | 25.6 | 30.1 | Pass; the two lines also differ by marker shape and dash |

"Other" / "Everyone else" is a neutral grey (`#c3c2bc`) and chart 4 uses a single ink colour, with
the year told apart by filled and hollow markers.

Some colours (aqua, yellow, pink) sit below 3:1 contrast against the white background, so the
charts write values on or beside every mark and give a table of values.
