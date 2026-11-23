"""Is frontier AI capability concentrating in fewer organisations?

Reads only data/processed/, which data_prep.py writes from data/raw/.
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_prep import NOT_STATED, OTHER, PARTIAL_YEAR, TOP_N

PROCESSED = Path(__file__).parent / "data" / "processed"

# One colour per company, the same in every chart. Each chart's set of
# colours was checked with a colour-vision-deficiency validator.
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
# Label colour inside each segment, chosen for contrast with the fill
TEXT_ON = {"Google": "#ffffff", "Microsoft": "#ffffff", "Amazon": "#ffffff"}
MUTED = "#6f6f6a"
GRID = "#e6e6e3"
SURFACE = "#ffffff"
HEADLINE_YEAR = PARTIAL_YEAR - 1

st.set_page_config(page_title="AI Concentration", page_icon="📊", layout="wide")


@st.cache_data
def read(name):
    return pd.read_csv(PROCESSED / name)


builders = read("builders_by_year.csv")
leaders = read("leaders_by_year.csv")
eci_top = read("eci_top_models.csv")
owned = read("chips_owned_by_quarter.csv")
used = read("chips_used_by_lab.csv")
facts = read("summary.csv").set_index("metric")["value"]

SOURCE_LINE = (
    f"**Source:** Epoch AI, epoch.ai/data (Notable AI Models, Epoch Capabilities Index, AI chip "
    f"owners, AI chip users), CC BY 4.0. **Last data refresh:** files downloaded "
    f"{pd.Timestamp(facts['data_downloaded']):%d %b %Y}; latest observation "
    f"{pd.Timestamp(facts['eci_latest']):%d %b %Y}."
)


def style(fig, title, x_title, y_title, legend_title=None, height=460):
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=16, color=INK)),
        height=height,
        margin=dict(l=10, r=130, t=90, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title=legend_title),
        xaxis=dict(title=x_title, showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED)),
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
                  line_width=0, layer="below")
    fig.add_annotation(x=PARTIAL_YEAR, y=0, yref="paper", yanchor="top", yshift=-22,
                       text="Jan to mid-Oct", showarrow=False, font=dict(color=MUTED, size=11))


def label_stack_ends(fig, x, last, value_col, name_col="company"):
    """Write each company's name beside its segment of the last bar."""
    bottom = 0
    for _, row in last.iterrows():
        # x is the bar's position on the axis; its right edge is under half a step away
        fig.add_annotation(x=x + 0.45, y=bottom + row[value_col] / 2, text=row[name_col],
                           showarrow=False, xanchor="left", xshift=4,
                           font=dict(color=INK, size=12))
        bottom += row[value_col]


def stacked_bar(fig, x, y, name, text, hover):
    fig.add_trace(go.Bar(
        x=x, y=y, name=name, marker_color=COLOR[name], marker_line=dict(color=SURFACE, width=1.5),
        text=text, textposition="inside", insidetextanchor="middle", textangle=0,
        textfont=dict(color=TEXT_ON.get(name, INK), size=12), hovertemplate=hover,
    ))


# Opening screen: the question, the whole package, the answer

st.title("Is frontier AI capability concentrating in fewer organisations?")
st.markdown(
    "**For:** a competition policy analyst deciding whether AI is becoming a market that a "
    "handful of firms control, and so whether it needs closer competition scrutiny."
)
st.caption(SOURCE_LINE)

chips_end = owned[owned["date"] == facts["chips_latest"]]
top4_share = chips_end.loc[chips_end["company"] != OTHER, "share_pct"].sum()
top10 = leaders[leaders["top_n"] == 10].groupby("year")["companies_in_top"].first()
top20 = leaders[leaders["top_n"] == 20].groupby("year")["companies_in_top"].first()
layer1 = builders.pivot(index="year", columns="company", values="share_pct").fillna(0)
orgs = builders.groupby("year")["organisations_in_year"].first()

st.subheader("What the whole dataset contains")
c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Notable models, 2019 to Oct {PARTIAL_YEAR}", f"{int(facts['notable_models'])}")
c1.caption(f"from {int(facts['notable_organisations'])} organisations")
c2.metric(f"Benchmarked models, 2023 to Oct {PARTIAL_YEAR}", f"{int(facts['eci_models'])}")
c2.caption(f"with an ECI score, from {int(facts['eci_companies'])} organisations")
c3.metric(f"Companies in the {HEADLINE_YEAR} ECI top 10", f"{top10[HEADLINE_YEAR]}")
c3.caption(f"down from {top10[2023]} in 2023")
c4.metric(f"AI chips owned by top 4, end {HEADLINE_YEAR}", f"{top4_share:.0f}%")
c4.caption("% of world H100e: Google, Microsoft, Amazon, Meta")

st.info(
    f"**Our answer: yes at the frontier, not across the whole field.** "
    f"The ten highest-scoring models of each year came from {top10[2023]} companies in 2023 "
    f"and {top10[HEADLINE_YEAR]} in {HEADLINE_YEAR} (top 20: {top20[2023]} to {top20[HEADLINE_YEAR]}), "
    f"and at the end of {HEADLINE_YEAR} four companies owned {top4_share:.0f}% of the world's AI "
    f"chips. But notable models in general still come from many organisations: "
    f"{orgs[HEADLINE_YEAR]} published at least one in {HEADLINE_YEAR}, and organisations outside "
    f"the five largest made {layer1.loc[HEADLINE_YEAR, OTHER]:.0f}% of them. "
    f"Someone who counts publishers could fairly answer *no*; this app argues the frontier "
    f"and the chips are what matter for competition."
)

# Layer 1

st.header("1. Notable models still come from many organisations")
st.markdown(
    f"Before ChatGPT, Google alone published a quarter of all notable models "
    f"({layer1.loc[2022, 'Google']:.0f}% in 2022). In the two years after it, organisations "
    f"outside the five largest took a bigger share ({layer1.loc[2024, OTHER]:.0f}% in 2024). "
    f"By {HEADLINE_YEAR} OpenAI led with {layer1.loc[HEADLINE_YEAR, 'OpenAI']:.0f}% and the "
    f"outside share fell back to {layer1.loc[HEADLINE_YEAR, OTHER]:.0f}%."
)
stack_order = ["Google", "OpenAI", "Anthropic", "Meta", "Alibaba", OTHER]
fig = go.Figure()
for company in stack_order:
    d = builders[builders["company"] == company]
    stacked_bar(fig, d["year"], d["share_pct"], company,
                [f"{v:.0f}%" if v >= 6 else "" for v in d["share_pct"]],
                f"<b>{company}</b>, %{{x}}<br>%{{y:.1f}}% of notable models<extra></extra>")
fig.update_layout(barmode="stack", bargap=0.25)
chatgpt_marker(fig, 2022.5)
partial_year(fig)
last = builders[builders["year"] == PARTIAL_YEAR].set_index("company").loc[stack_order].reset_index()
label_stack_ends(fig, PARTIAL_YEAR, last, "share_pct")
style(fig, "Share of each year's notable models, by organisation (%), 2019 to mid-October 2026",
      "Publication year", "Share of the year's notable models (%)", "Organisation (share of models, %)")
fig.update_xaxes(dtick=1, range=[2018.5, PARTIAL_YEAR + 0.5])
fig.update_yaxes(range=[0, 100], ticksuffix="%")
st.plotly_chart(fig, config={"displayModeBar": False})
st.caption(
    "Other = every organisation outside the five that published the most notable models from "
    "2019 to 2026. A model built by several organisations is split evenly between them. "
    "Segments under 6% are unlabelled on the chart; every value is in the table below."
)
table = layer1[stack_order].round(1)
table.index.name = "Year"
table["Organisations publishing"] = orgs
st.dataframe(table.rename(columns=lambda c: f"{c} (%)" if c in stack_order else c),
             width="stretch")

# Layer 2

# A fragment reruns only this layer when its controls change, so the
# ranking toggle and year slider respond without redrawing the whole page
@st.fragment
def layer_two():
    st.header("2. Three companies hold the top of the benchmark ranking")
    top_n = st.radio("Size of the ranking", TOP_N, index=0, horizontal=True,
                     format_func=lambda n: f"Top {n} models each year")
    st.markdown(
        f"The Epoch Capabilities Index (ECI) combines many benchmarks into one score. Ranking each "
        f"year's releases by ECI, the top {top_n} came from "
        f"{leaders.query('top_n == @top_n and year == 2023')['companies_in_top'].iloc[0]} companies "
        f"in 2023 and {leaders.query('top_n == @top_n and year == @HEADLINE_YEAR')['companies_in_top'].iloc[0]} "
        f"in {HEADLINE_YEAR}."
    )
    board = leaders[leaders["top_n"] == top_n]
    slot_order = ["Google", "OpenAI", "Anthropic", OTHER]
    bar = go.Figure()
    for company in slot_order:
        d = board[board["company"] == company]
        stacked_bar(bar, d["year"], d["places"], company, [f"{v:g}" for v in d["places"]],
                    f"<b>{company}</b>, %{{x}}<br>%{{y:g}} of the top {top_n}<extra></extra>")
    for year, n in board.groupby("year")["companies_in_top"].first().items():
        bar.add_annotation(x=year, y=top_n, text=f"{n} companies", showarrow=False, yanchor="bottom",
                           yshift=4, font=dict(color=INK, size=13))
    bar.update_layout(barmode="stack", bargap=0.35)
    partial_year(bar)
    last = board[board["year"] == PARTIAL_YEAR].set_index("company").reindex(slot_order).dropna(subset=["places"]).reset_index()
    label_stack_ends(bar, PARTIAL_YEAR, last, "places")
    style(bar, f"Models in each year's top {top_n} by ECI score, by company (count), 2023 to mid-October 2026",
          "Release year", f"Models in the year's top {top_n} (count)", f"Company (models in top {top_n})")
    bar.update_xaxes(dtick=1, range=[2022.5, PARTIAL_YEAR + 0.5])
    bar.update_yaxes(range=[0, top_n * 1.1])
    st.plotly_chart(bar, config={"displayModeBar": False})
    others = sorted(set(eci_top.loc[eci_top["rank"] <= top_n, "Company"]) - set(slot_order) - {NOT_STATED})
    st.caption(
        f"Epoch only publishes ECI scores for models released from 2023 onwards, after ChatGPT's "
        f"launch. Other = {', '.join(others)}, plus models whose organisation the source does not "
        f"state. The company count leaves those models out."
    )
    year = st.select_slider(f"Show the top {top_n} models of", options=sorted(eci_top["year"].unique()),
                            value=HEADLINE_YEAR)
    chosen = eci_top[(eci_top["year"] == year) & (eci_top["rank"] <= top_n)]
    if chosen.empty:
        st.info(f"No models with an ECI score were released in {year}. Pick another year.")
    else:
        st.dataframe(chosen[["rank", "Model", "Company", "date", "eci"]]
                     .rename(columns={"rank": "Rank", "date": "Release date", "eci": "ECI score (index points)"}),
                     hide_index=True, width="stretch")


layer_two()

# Layer 3

st.header("3. Four companies own most of the AI chips")
snapshots = sorted(owned["date"].unique())
snapshots = [snapshots[0]] + [d for d in snapshots if d.endswith("-12-31")]
shares = owned[owned["date"].isin(snapshots)].copy()
shares["label"] = pd.to_datetime(shares["date"]).dt.strftime("End %b %Y")
labels = list(dict.fromkeys(shares.sort_values("date")["label"]))
st.markdown(
    f"At the end of {HEADLINE_YEAR}, Google, Microsoft, Amazon and Meta together owned "
    f"{top4_share:.0f}% of the world's AI chips, measured in H100-equivalents (H100e: computing "
    f"power expressed as a number of Nvidia H100 chips). OpenAI and Anthropic, two of the three "
    f"benchmark leaders, are not among the owners in Epoch's data."
)
owner_order = ["Google", "Microsoft", "Amazon", "Meta", OTHER]
chips = go.Figure()
for company in owner_order:
    d = shares[shares["company"] == company].set_index("label").loc[labels].reset_index()
    name = "Everyone else" if company == OTHER else company
    chips.add_trace(go.Bar(
        x=d["label"], y=d["share_pct"], name=name, marker_color=COLOR[company],
        marker_line=dict(color=SURFACE, width=1.5),
        text=[f"{v:.0f}%" for v in d["share_pct"]], textposition="inside",
        insidetextanchor="middle", textangle=0, textfont=dict(color=TEXT_ON.get(company, INK), size=12),
        customdata=d["h100e"] / 1e6,
        hovertemplate=f"<b>{name}</b>, %{{x}}<br>%{{y:.1f}}% (%{{customdata:.2f}} million H100e)<extra></extra>",
    ))
totals = shares.groupby("label")["h100e"].sum().loc[labels] / 1e6
for label, total in totals.items():
    chips.add_annotation(x=label, y=100, text=f"Total {total:.2f}M H100e", showarrow=False,
                         yanchor="bottom", yshift=4, font=dict(color=INK, size=12))
chips.update_layout(barmode="stack", bargap=0.35)
chatgpt_marker(chips, 0.5)
last = shares[shares["label"] == labels[-1]].set_index("company").loc[owner_order].reset_index()
last["name"] = last["company"].replace({OTHER: "Everyone else"})
label_stack_ends(chips, len(labels) - 1, last, "share_pct", "name")
style(chips, "Share of the world's AI chips owned, by owner (% of H100e), March 2022 to December 2025",
      "Quarter end", "Share of AI chips owned (% of H100e)", "Owner (share of H100e, %)")
# Headroom above the bars keeps the totals clear of the ChatGPT label
chips.update_yaxes(range=[0, 128], tickvals=[0, 20, 40, 60, 80, 100], ticksuffix="%")
st.plotly_chart(chips, config={"displayModeBar": False})
st.caption(
    "Epoch's median estimate of the chips each owner held at quarter end. Everyone else = Oracle, "
    "CoreWeave, xAI, owners in China and all other owners. The first bar is the earliest quarter "
    "Epoch covers; Q1 2026 is left out because Epoch marks it incomplete."
)

labs = used[used["Year"] >= 2024].copy()
order = labs[labs["Year"] == 2025].sort_values("h100e_med")["company"].tolist()
dots = go.Figure()
for yr, symbol, position in [(2024, "circle-open", "bottom center"), (2025, "circle", "top center")]:
    d = labs[labs["Year"] == yr].set_index("company").loc[order].reset_index()
    dots.add_trace(go.Scatter(
        x=d["h100e_med"] / 1e6, y=d["company"], mode="markers+text", name=f"End {yr}",
        marker=dict(color=INK, size=11, symbol=symbol, line=dict(color=INK, width=2)),
        text=[f"{v / 1e6:.2f}M" for v in d["h100e_med"]], textposition=position,
        textfont=dict(color=INK, size=12),
        error_x=dict(type="data", symmetric=False, color=MUTED, thickness=1.5, width=0,
                     array=(d["h100e_p95"] - d["h100e_med"]) / 1e6,
                     arrayminus=(d["h100e_med"] - d["h100e_p5"]) / 1e6),
        hovertemplate=f"<b>%{{y}}</b>, end {yr}<br>%{{x:.2f}} million H100e<extra></extra>",
    ))
style(dots, "Compute each frontier lab could use, owned or rented (million H100e), end 2024 and end 2025",
      "Compute available (million H100e; line = 5th to 95th percentile)", "Lab", "Median estimate (million H100e)", height=400)
dots.update_layout(margin=dict(r=20))
dots.update_xaxes(showgrid=True, gridcolor=GRID, rangemode="tozero")
dots.update_yaxes(gridcolor=SURFACE)
st.plotly_chart(dots, config={"displayModeBar": False})
ranges = labs.assign(**{
    "Lab": labs["company"],
    "Median (M H100e)": labs["h100e_med"] / 1e6,
    "5th percentile": labs["h100e_p5"] / 1e6,
    "95th percentile": labs["h100e_p95"] / 1e6,
})[["Lab", "Year", "Median (M H100e)", "5th percentile", "95th percentile"]].round(2)
st.dataframe(ranges.sort_values(["Year", "Median (M H100e)"], ascending=[True, False]),
             hide_index=True, width="stretch")
st.caption(
    "Epoch's estimate of the compute available to each lab, whoever owns the chips. The ranges are "
    "wide and overlap: treat the order of nearby labs as uncertain."
)

# Limits and method

st.header("What this data cannot show")
st.markdown(f"""
- **Market power.** Shares of models, benchmark places and chips are not shares of revenue, users or
  profit. The app shows who builds and who owns, not who earns.
- **Causes.** The ChatGPT line marks timing only. Nothing here shows that the launch caused the changes after it.
- **Every model.** "Notable" is Epoch's own selection, and ECI covers only models Epoch has benchmark
  results for, from 2023. Three 2023 top-20 models have no organisation in Epoch's file and are left
  out of the company count.
- **Training compute.** It is missing for most recent models ({float(facts['compute_known_pct_2026']):g}% of
  {PARTIAL_YEAR} models have a figure), and Google has a figure for only
  {int(facts['google_models_with_compute_2025'])} of its {int(facts['google_models_2025'])} notable 2025
  models. So the app counts models, not compute: compute shares would show Google vanishing.
- **Exact chip numbers.** Chip holdings are estimates with wide uncertainty ranges. Q1 2026 is incomplete.
- **A full 2026.** {PARTIAL_YEAR} runs only to mid-October.
""")

with st.expander("Data and method"):
    st.markdown("""
The app reads only `data/processed/`. `python data_prep.py` rebuilds those tables from the
unchanged Epoch AI files in `data/raw/`; `data/DATA_DICTIONARY.md` describes every file and column.

1. Split each model's organisation list on commas and share the model evenly between them.
2. Merge labs of the same company: Google Brain, Google Research and DeepMind count as Google;
   Facebook AI Research and Meta AI count as Meta; Epoch's "SpaceXAI" counts as xAI.
3. Layer 1: add up each organisation's share of the year's notable models.
4. Layer 2: rank each year's releases by ECI score, take the top 10 or 20, count the companies.
5. Layer 3: add up each owner's chips across chip designers (Nvidia, Google TPU, Amazon and so on).
""")
st.caption(SOURCE_LINE)
