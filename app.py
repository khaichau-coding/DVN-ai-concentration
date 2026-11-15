import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_prep import (
    CHATGPT_LAUNCH,
    OTHER,
    PARTIAL_YEAR,
    builders_by_year,
    builders_count,
    chips_owned,
    chips_used,
    eci_top10,
    leaders_by_year,
    load_eci,
    load_notable,
)

# One colour per company, the same in every chart. Checked with the
# dataviz palette validator for each chart's set of companies.
COLOR = {
    "Google": "#2a78d6",
    "OpenAI": "#eb6834",
    "Anthropic": "#1baf7a",
    "Meta": "#eda100",
    "Alibaba": "#e87ba4",
    "Microsoft": "#008300",
    "Amazon": "#e34948",
    OTHER: "#c3c2bc",
}
INK = "#3d3d3a"
MUTED = "#8a8a85"
GRID = "#e6e6e3"
SURFACE = "#ffffff"
HEADLINE_YEAR = PARTIAL_YEAR - 1

st.set_page_config(page_title="AI Concentration", page_icon="📊", layout="wide")


@st.cache_data
def tables():
    notable, eci = load_notable(), load_eci()
    return (notable, eci, builders_by_year(notable), leaders_by_year(eci),
            chips_owned(), chips_used())


notable, eci, builders, leaders, owned, used = tables()


def style(fig, y_title, height=440):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=120, t=40, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, size=14),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, traceorder="normal"),
        xaxis=dict(showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED)),
        yaxis=dict(title=y_title, gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED)),
    )
    return fig


def chatgpt_marker(fig, x):
    fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=1, yref="paper",
                  line=dict(color=INK, width=1.5, dash="dash"))
    fig.add_annotation(x=x, y=1, yref="paper", text="ChatGPT launch<br>30 Nov 2022",
                       showarrow=False, xanchor="left", yanchor="top", xshift=6,
                       font=dict(color=INK, size=12), align="left", bgcolor=SURFACE)


def partial_year(fig):
    fig.add_vrect(x0=PARTIAL_YEAR - 0.5, x1=PARTIAL_YEAR + 0.5, fillcolor=GRID, opacity=0.45,
                  line_width=0, layer="below", annotation_text="Jan–mid Oct",
                  annotation_position="top", annotation_font=dict(color=MUTED, size=11))


def label_stack_ends(fig, last, value_col):
    """Write each company's name beside its segment of the last bar."""
    bottom = 0
    for _, row in last.iterrows():
        fig.add_annotation(x=last["year"].iloc[0], y=bottom + row[value_col] / 2,
                           text=row["company"], showarrow=False, xanchor="left",
                           xshift=34, font=dict(color=INK, size=12))
        bottom += row[value_col]


st.title("Is frontier AI capability concentrating in fewer organisations?")
st.markdown(
    "**For:** a competition policy analyst deciding whether AI is becoming a market "
    "that a handful of firms control."
)
st.markdown(
    "The answer changes with the layer you look at. Many organisations publish notable "
    "models. Very few build the most capable ones. The chips those models run on sit "
    "with a handful of companies."
)

orgs_now = builders_count(notable, HEADLINE_YEAR)
companies = leaders.groupby("year")["companies_in_top10"].first()
end = owned[owned["date"] == owned["date"].max()]
top4_share = end[end["company"] != OTHER]["share"].sum()

c1, c2, c3 = st.columns(3)
c1.metric(f"Organisations with a notable model, {HEADLINE_YEAR}", orgs_now)
c2.metric(f"Companies in the benchmark top 10, {HEADLINE_YEAR}", companies[HEADLINE_YEAR],
          f"{companies[HEADLINE_YEAR] - companies[2023]} since 2023", delta_color="off")
c3.metric(f"AI chips owned by four companies, end {owned['date'].max().year}",
          f"{top4_share:.0f}%")

# Layer 1
st.header("1. Many organisations build notable models")
share = builders.pivot(index="year", columns="company", values="share").fillna(0)
st.markdown(
    f"Before ChatGPT, Google alone published a quarter of all notable models "
    f"({share.loc[2022, 'Google']:.0f}% in 2022). In the two years after it, organisations "
    f"outside the top five took a bigger share ({share.loc[2024, OTHER]:.0f}% in 2024). "
    f"By {HEADLINE_YEAR} OpenAI had taken the lead and the outside share fell back to "
    f"{share.loc[HEADLINE_YEAR, OTHER]:.0f}%."
)
stack_order = ["Google", "OpenAI", "Anthropic", "Meta", "Alibaba", OTHER]
fig = go.Figure()
for company in stack_order:
    d = builders[builders["company"] == company]
    fig.add_trace(go.Bar(
        x=d["year"], y=d["share"], name=company, marker_color=COLOR[company],
        marker_line=dict(color=SURFACE, width=1.5), customdata=d["models"],
        hovertemplate=f"<b>{company}</b>, %{{x}}<br>%{{y:.0f}}% of notable models "
                      "(%{customdata:.0f} models)<extra></extra>",
    ))
fig.update_layout(barmode="stack", bargap=0.25)
chatgpt_marker(fig, 2022.5)
partial_year(fig)
last = builders[builders["year"] == PARTIAL_YEAR].set_index("company").loc[stack_order].reset_index()
label_stack_ends(fig, last, "share")
style(fig, "Share of the year's notable models (%)")
fig.update_xaxes(dtick=1)
fig.update_yaxes(range=[0, 100], ticksuffix="%")
st.plotly_chart(fig)
st.caption(
    "Other = every organisation outside the five that published the most notable models "
    "from 2019 to 2026. A model built by several organisations is split evenly between them."
)
with st.expander("Show the numbers"):
    counts = builders.pivot(index="year", columns="company", values="models").fillna(0)
    st.dataframe(counts[stack_order].round(1), width="stretch")

# Layer 2
st.header("2. Only three companies build the most capable models")
st.markdown(
    f"The Epoch Capabilities Index (ECI) combines many benchmarks into one score. Take the ten "
    f"highest-scoring models of each year: in 2023 they came from {companies[2023]} companies; "
    f"in {HEADLINE_YEAR}, from just {companies[HEADLINE_YEAR]}: OpenAI, Google and Anthropic."
)
slot_order = ["Google", "OpenAI", "Anthropic", OTHER]
bar = go.Figure()
for company in slot_order:
    d = leaders[leaders["company"] == company]
    bar.add_trace(go.Bar(
        x=d["year"], y=d["slots"], name=company, marker_color=COLOR[company],
        marker_line=dict(color=SURFACE, width=1.5),
        hovertemplate=f"<b>{company}</b>, %{{x}}<br>%{{y:.0f}} of the top 10<extra></extra>",
    ))
for year, n in companies.items():
    bar.add_annotation(x=year, y=10, text=f"{n} companies", showarrow=False, yanchor="bottom",
                       yshift=4, font=dict(color=INK, size=13))
bar.update_layout(barmode="stack", bargap=0.35)
partial_year(bar)
last = leaders[leaders["year"] == PARTIAL_YEAR].set_index("company").reindex(slot_order).dropna(subset=["slots"]).reset_index()
label_stack_ends(bar, last, "slots")
style(bar, "Models in the year's top 10")
bar.update_xaxes(dtick=1)
bar.update_yaxes(range=[0, 11], dtick=2)
st.plotly_chart(bar)
st.caption(
    "Epoch only publishes ECI scores for models released from 2023 onwards, after ChatGPT's "
    "launch. Other = Mistral AI, 01.AI, Stability AI, DeepSeek, Microsoft and xAI."
)
year = st.select_slider("Show the top 10 of", options=sorted(eci["year"].unique()), value=HEADLINE_YEAR)
st.dataframe(eci_top10(eci, year)[["Model", "Company", "date", "eci"]]
             .rename(columns={"date": "Release date", "eci": "ECI score"}), width="stretch")

# Layer 3
st.header("3. The chips sit with a handful of companies")
st.markdown(
    f"At the end of {owned['date'].max().year}, Google, Microsoft, Amazon and Meta together "
    f"owned {top4_share:.0f}% of the world's AI chips, measured in H100-equivalents "
    f"(computing power expressed as a number of Nvidia H100 chips). "
    "OpenAI and Anthropic, two of the three capability leaders, are not among the owners."
)
lines = go.Figure()
label_y = {}
for company in ["Google", "Microsoft", "Amazon", "Meta", OTHER]:
    d = owned[owned["company"] == company]
    name = "Everyone else" if company == OTHER else company
    lines.add_trace(go.Scatter(
        x=d["date"], y=d["h100e"] / 1e6, name=name, mode="lines",
        line=dict(color=COLOR[company], width=2, dash="dot" if company == OTHER else "solid"),
        hovertemplate=f"<b>{name}</b><br>%{{y:.2f}} million H100e<extra></extra>",
    ))
    label_y[name] = d["h100e"].iloc[-1] / 1e6
# Push end labels apart so lines that finish close together stay readable
placed = []
for name, y in sorted(label_y.items(), key=lambda kv: kv[1]):
    y = max(y, placed[-1] + 0.3) if placed else y
    placed.append(y)
    lines.add_annotation(x=owned["date"].max(), y=y, text=name, showarrow=False,
                         xanchor="left", xshift=8, font=dict(color=INK, size=12))
chatgpt_marker(lines, CHATGPT_LAUNCH)
style(lines, "AI chips owned (million H100e)")
lines.update_layout(hovermode="x unified")
st.plotly_chart(lines)
st.caption(
    "End-of-quarter stock, Epoch's median estimate. Everyone else = Oracle, CoreWeave, xAI, "
    "owners in China and all other owners. Q1 2026 is left out because Epoch marks it incomplete."
)
with st.expander("Show the numbers"):
    table = owned.pivot(index="date", columns="company", values="h100e")
    table.index = table.index.date
    st.dataframe((table / 1e6).round(2), width="stretch")

st.subheader("Compute each frontier lab could use, owned or rented")
labs = used[used["Year"] >= 2024].copy()
order = labs[labs["Year"] == 2025].sort_values("h100e_med")["company"].tolist()
dots = go.Figure()
for yr, symbol in [(2024, "circle-open"), (2025, "circle")]:
    d = labs[labs["Year"] == yr].set_index("company").loc[order].reset_index()
    dots.add_trace(go.Scatter(
        x=d["h100e_med"] / 1e6, y=d["company"], mode="markers", name=f"End {yr}",
        marker=dict(color=INK, size=11, symbol=symbol, line=dict(color=INK, width=2)),
        error_x=dict(type="data", symmetric=False, color=MUTED, thickness=1.5, width=0,
                     array=(d["h100e_p95"] - d["h100e_med"]) / 1e6,
                     arrayminus=(d["h100e_med"] - d["h100e_p5"]) / 1e6),
        customdata=d[["h100e_p5", "h100e_p95"]] / 1e6,
        hovertemplate=f"<b>%{{y}}</b>, end {yr}<br>%{{x:.2f}} million H100e"
                      "<br>range %{customdata[0]:.2f}–%{customdata[1]:.2f}<extra></extra>",
    ))
style(dots, None, height=340)
dots.update_layout(margin=dict(r=20))
dots.update_xaxes(title="Million H100e (line = 5th to 95th percentile)", showgrid=True, gridcolor=GRID)
dots.update_yaxes(gridcolor=SURFACE)
st.plotly_chart(dots)
st.caption(
    "Epoch's estimate of the compute available to each lab, whoever owns the chips. "
    "The ranges are wide: treat the order of nearby labs as uncertain."
)

compute_known = notable.loc[notable["year"] == PARTIAL_YEAR, "Training compute (FLOP)"].notna().mean() * 100
with st.expander("Data and method"):
    st.markdown(f"""
**Sources.** All from Epoch AI (epoch.ai/data), downloaded on 27 October 2026, Creative Commons
Attribution licence. The files are kept unchanged in `data/raw/`.

| Layer | File | What it holds |
|---|---|---|
| 1 | `notable_ai_models.csv` | {len(notable)} notable models published from {notable['year'].min()} |
| 2 | `benchmark_data/eci_scores.csv` | ECI scores for {len(eci)} models released from 2023 |
| 3 | `ai_chip_owners/cumulative_by_designer.csv` | AI chips owned, by owner and quarter, from 2022 |
| 3 | `ai_chip_users/year_end_by_lab.csv` | Compute available to five frontier labs, 2023–2025 |

**Steps** (all in `data_prep.py`):
1. Split the organisation column on commas, so a joint model gives one row per organisation,
   and split the model evenly between them.
2. Merge labs of the same company: Google Brain, Google Research and DeepMind count as Google;
   Facebook AI Research and Meta AI count as Meta; Epoch's "SpaceXAI" counts as xAI.
3. Layer 1: add up each organisation's share of the year's notable models.
4. Layer 2: take each year's ten highest ECI scores and count the companies behind them.
5. Layer 3: add up each owner's chips across chip designers (Nvidia, Google TPU, Amazon and so on).

**Why notable models are counted, not their training compute.** Training compute is
missing for most recent models (Epoch has a figure for only {compute_known:.0f}% of {PARTIAL_YEAR}
models), and Google has
not published it for its Gemini models since 2024. Shares of compute would show Google
vanishing, which is an artefact of disclosure, not of the market.

**Limits.** "Notable" is Epoch's selection, so layer 1 describes what Epoch tracks, not every
model released. ECI covers the models Epoch has benchmark results for. Chip figures are
estimates with wide uncertainty. {PARTIAL_YEAR} runs only to mid-October.
""")
