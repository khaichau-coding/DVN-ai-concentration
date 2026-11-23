"""Frontier gap: how far behind the leading group are the others?

Reads only data/processed/, which data_prep.py writes from data/raw/.
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_prep import COMPARISONS

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"

# Leading group in violet (a colour no company uses on the main page),
# chasing group in neutral grey with a dashed line, so the two also differ
# by line style and never rely on colour alone
LEADING = "#6250d6"
CHASING = "#8a8a85"
INK = "#3d3d3a"
MUTED = "#6f6f6a"
GRID = "#e6e6e3"

st.set_page_config(page_title="Frontier Gap | AI Concentration", page_icon="📊", layout="wide")


@st.cache_data
def read(name, dates=()):
    return pd.read_csv(PROCESSED / name, parse_dates=list(dates))


models = read("eci_frontier_models.csv", ["date"])
gaps = read("frontier_gap.csv", ["period_end"])
facts = read("summary.csv").set_index("metric")["value"]

st.title("5. Frontier gap: how far behind are the others?")
st.markdown(
    "**For a competition policy analyst:** a handful of companies hold the top of the benchmark "
    "ranking, but is their lead growing? If the best models from everyone else stay only a few "
    "months behind, the frontier is crowded at the top rather than locked up."
)
st.caption(
    f"**Source:** Epoch AI, Epoch Capabilities Index (epoch.ai/benchmarks), CC BY 4.0. "
    f"**Last data refresh:** files downloaded {pd.Timestamp(facts['data_downloaded']):%d %b %Y}; "
    f"latest model {pd.Timestamp(facts['eci_latest']):%d %b %Y}."
)

c1, c2 = st.columns([1, 1])
with c1:
    comparison = st.radio("Compare", list(COMPARISONS), horizontal=True)
with c2:
    years = st.slider("Release years shown", 2023, int(models["date"].dt.year.max()), (2023, 2026))

leading_name, chasing_name = COMPARISONS[comparison]
shown = models[(models["comparison"] == comparison) & models["date"].dt.year.between(*years)]
lead, chase = shown[shown["role"] == "leading"], shown[shown["role"] == "chasing"]
table = gaps[(gaps["comparison"] == comparison) & gaps["period_end"].dt.year.between(*years)]

if lead.empty or chase.empty or table.empty:
    st.info("There are no models from both groups in these years. Widen the year range to compare them.")
    st.stop()

latest = table.iloc[-1]
end = min(pd.Timestamp(f"{years[1]}-12-31"), models["date"].max())
lagged = table.dropna(subset=["months_behind"])
st.markdown(
    f"**What this shows.** By {latest['period_end']:%d %b %Y}, the best {leading_name.split(':')[0].lower()} "
    f"model scored **{latest['leading_best_eci']:.1f}** ECI points and the best from "
    f"{chasing_name.lower()} **{latest['chasing_best_eci']:.1f}**, a gap of "
    f"**{latest['gap_eci']:.1f} points**. "
    + (f"That best chasing model matched a score the leading group first reached "
       f"**{latest['months_behind']:.0f} months** earlier. " if pd.notna(latest["months_behind"]) else "")
    + (f"From {lagged.iloc[0]['period_end']:%b %Y} the gap moved between "
       f"{lagged['gap_eci'].min():.1f} and {lagged['gap_eci'].max():.1f} points and the lag between "
       f"{lagged['months_behind'].min():.0f} and {lagged['months_behind'].max():.0f} months; "
       f"it was {lagged.iloc[0]['gap_eci']:.1f} points then and {latest['gap_eci']:.1f} at the latest date."
       if len(lagged) > 1 else "")
)

fig = go.Figure()
for df, name, color, dash in [(chase, chasing_name, CHASING, "dash"), (lead, leading_name, LEADING, "solid")]:
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["eci"], mode="markers", name=f"{name}: each model",
        marker=dict(color=color, size=7, opacity=0.35, line=dict(width=0)),
        customdata=df[["Model"]],
        hovertemplate="<b>%{customdata[0]}</b><br>%{x|%d %b %Y}<br>ECI %{y:.1f}<extra></extra>",
    ))
    # Best score so far: a step that only rises when a model beats it
    step = pd.concat([df[["date", "best_so_far"]],
                      pd.DataFrame({"date": [end], "best_so_far": [df["best_so_far"].iloc[-1]]})])
    fig.add_trace(go.Scatter(
        x=step["date"], y=step["best_so_far"], mode="lines", line_shape="hv", name=f"{name}: best so far",
        line=dict(color=color, width=2.5, dash=dash),
        hovertemplate=f"{name}<br>best so far %{{y:.1f}}<extra></extra>",
    ))
    fig.add_annotation(x=step["date"].iloc[-1], y=step["best_so_far"].iloc[-1],
                       text=f"{df['best_so_far'].iloc[-1]:.1f}", showarrow=False, xanchor="left",
                       xshift=8, font=dict(color=INK, size=13))

fig.add_shape(type="line", x0=end, x1=end, y0=latest["chasing_best_eci"], y1=latest["leading_best_eci"],
              line=dict(color=INK, width=1.5))
fig.add_annotation(x=end, y=(latest["chasing_best_eci"] + latest["leading_best_eci"]) / 2,
                   text=f"gap {latest['gap_eci']:.1f}", showarrow=False, xanchor="left", xshift=50,
                   font=dict(color=INK, size=13))
fig.update_layout(
    title=dict(text=f"Best ECI score reached so far: {leading_name} vs {chasing_name.lower()}, "
                    f"{years[0]} to {end:%b %Y}", x=0, font=dict(size=16, color=INK)),
    height=520, margin=dict(l=10, r=110, t=130, b=10),
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color=INK, size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title="Group (ECI index points)"),
    xaxis=dict(title="Model release date", showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED)),
    yaxis=dict(title="ECI score (index points)", gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED)),
)
st.plotly_chart(fig, config={"displayModeBar": False})
st.caption(
    "Each faint dot is one model; the lines step up when a model beats its group's best so far. "
    "Values at the right are each group's best score at the end of the period shown. Every dot's "
    "model, date and score is listed in the table further down."
)

st.subheader("The gap at each half-year end")
st.dataframe(
    table.assign(**{
        "Period end": table["period_end"].dt.strftime("%d %b %Y"),
        "Leading best (ECI)": table["leading_best_eci"],
        "Chasing best (ECI)": table["chasing_best_eci"],
        "Gap (ECI points)": table["gap_eci"],
        "Months behind": table["months_behind"].map(lambda v: "" if pd.isna(v) else f"{v:.1f}"),
        "Best chasing model": table["chasing_best_model"],
        "First leading model at that score": table["leading_first_reached_model"],
    })[["Period end", "Leading best (ECI)", "Chasing best (ECI)", "Gap (ECI points)", "Months behind",
        "Best chasing model", "First leading model at that score"]],
    hide_index=True, width="stretch",
)
st.caption(
    "Months behind = release date of the chasing group's best model minus the date the leading group "
    "first released a model with at least that score. Blank for mid-2023: ECI starts in February 2023, "
    "so the leading group's earlier models are not scored. The last row is the latest data, mid-October 2026."
)

# Every dot on the chart with its exact score, so no value needs hovering
st.subheader(f"Every model in the chart ({len(shown)} models)")
st.dataframe(
    shown.sort_values("date", ascending=False).assign(**{
        "Release date": shown["date"].dt.strftime("%d %b %Y"),
        "Group": shown["group"],
        "ECI score (index points)": shown["eci"],
        "Group best so far (ECI)": shown["best_so_far"],
        "New group best": shown["is_record"].map({True: "Yes", False: ""}),
    })[["Release date", "Model", "Organization", "Group", "ECI score (index points)",
        "Group best so far (ECI)", "New group best"]],
    hide_index=True, width="stretch", height=320,
)

st.subheader("What this data cannot show")
st.markdown("""
- **Every model.** ECI covers only models Epoch has benchmark results for, from February 2023.
- **Models with no stated organisation** (including Google's PaLM 2) are left out of the Top 3
  comparison; models with unknown or limited access are left out of the weights comparison.
- **Quality beyond benchmarks.** A gap in ECI points says nothing about cost, reliability or how many
  people use a model.
- **Why the gap moves as it does.** Imitation, distillation, open publishing, investment and talent moves
  could all play a part; the data does not say which.
""")
