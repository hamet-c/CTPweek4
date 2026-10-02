"""Streamlit dashboard for the Week 4 MovieLens analysis.

Run with:  streamlit run app.py
Numbers come from analysis.py; charts here are interactive Altair versions of
the PNGs that analysis.py saves to charts/.
"""
import re

import altair as alt
import pandas as pd
import streamlit as st

import analysis as a

st.set_page_config(page_title="Movie Ratings Dashboard", page_icon="🎬", layout="wide")

# --- Palette (dark) ---------------------------------------------------------
# Data marks: gold = "best", blue = default series / lowest, slate = everything else.
# Gold + blue validated together on SURFACE (CVD and normal-vision separation pass).
GOLD = "#c98500"         # data marks
GOLD_UI = "#f2b632"      # chrome only: badges, accents, slider
BLUE = "#3987e5"
SLATE = "#5b6479"
SURFACE = "#252d3f"
TEXT = "#e8e6df"
TEXT_2 = "#b6bbc8"
MUTED = "#8189a0"
GRID = "#313a51"
AXIS = "#454f68"
FONT = "Inter, system-ui, sans-serif"

st.markdown(f"""
<style>
.block-container {{ padding-top: 2.2rem; max-width: 1280px; }}
[data-testid="stHeader"] {{ background: transparent; }}
h2, h3 {{ letter-spacing: -0.01em; }}

.hero {{ padding: 8px 0 18px; }}
.hero .eyebrow {{ color: {GOLD_UI}; font-weight: 600; font-size: .8rem;
  letter-spacing: .14em; text-transform: uppercase; }}
.hero .title {{ font-size: 2.6rem; font-weight: 800; margin: .25rem 0 .4rem; line-height: 1.15;
  letter-spacing: -0.025em; color: {TEXT}; }}
.hero .title span {{ color: {GOLD_UI}; }}
.hero p {{ color: {TEXT_2}; font-size: 1.02rem; margin: 0; max-width: 760px; }}

.kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 6px 0 14px; }}
.kpi {{ background: {SURFACE}; border: 1px solid {GRID}; border-radius: 14px; padding: 16px 18px; }}
.kpi .label {{ color: {TEXT_2}; font-size: .82rem; }}
.kpi .value {{ color: {TEXT}; font-size: 1.85rem; font-weight: 700; margin-top: 2px; }}
.kpi .value .star {{ color: {GOLD_UI}; font-size: 1.3rem; }}
@media (max-width: 760px) {{ .kpis {{ grid-template-columns: repeat(2, 1fr); }} }}

.nav {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 26px; }}
.nav a {{ color: {TEXT_2}; text-decoration: none; font-size: .88rem; font-weight: 500;
  padding: 6px 14px; border: 1px solid {AXIS}; border-radius: 999px; }}
.nav a:hover {{ color: {GOLD_UI}; border-color: {GOLD_UI}; }}

.qhead {{ margin: 34px 0 10px; scroll-margin-top: 70px; }}
.qhead .tag {{ display: inline-block; color: {GOLD_UI}; font-weight: 700; font-size: .78rem;
  letter-spacing: .1em; }}
.qhead h2 {{ font-size: 1.55rem; font-weight: 700; margin: .15rem 0 .2rem; padding: 0; }}
.qhead p {{ color: {TEXT_2}; margin: 0; }}

.answer {{ border-left: 3px solid {GOLD_UI}; background: {SURFACE}; border-radius: 0 12px 12px 0;
  padding: 14px 18px; color: {TEXT}; line-height: 1.6; margin-top: 8px; }}
.answer b {{ color: #ffffff; font-weight: 700; }}
.answer .best {{ color: {GOLD_UI}; font-weight: 700; }}

.big {{ font-size: 3rem; font-weight: 800; color: {GOLD_UI}; line-height: 1; }}
.bigcap {{ color: {TEXT_2}; font-size: .92rem; margin-top: 6px; }}

.rank-list {{ display: flex; flex-direction: column; gap: 6px; }}
.rank-row {{ display: flex; align-items: center; gap: 10px; background: {SURFACE};
  border: 1px solid {GRID}; border-radius: 10px; padding: 8px 12px; }}
.rank-row .dot {{ width: 10px; height: 10px; border-radius: 50%; flex: none; }}
.rank-row .name {{ flex: 1; color: {TEXT}; }}
.rank-row .val {{ color: {TEXT}; font-weight: 600; font-variant-numeric: tabular-nums; }}
.rank-row .n {{ color: {MUTED}; font-size: .8rem; width: 92px; text-align: right; }}

.floor-head {{ display: flex; align-items: baseline; justify-content: space-between; margin: 4px 0 10px; }}
.floor-head .t {{ font-weight: 700; font-size: 1.08rem; color: {TEXT}; }}
.floor-head .s {{ color: {MUTED}; font-size: .85rem; }}
.movie {{ display: flex; align-items: center; gap: 14px; padding: 12px 14px; margin-bottom: 8px;
  background: {SURFACE}; border: 1px solid {GRID}; border-radius: 12px; }}
.movie.keep {{ border-color: rgba(242,182,50,.55); background: linear-gradient(90deg, rgba(242,182,50,.10), {SURFACE} 55%); }}
.movie .rank {{ width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center;
  font-weight: 800; flex: none; background: #364055; color: {TEXT_2}; }}
.movie.keep .rank {{ background: {GOLD_UI}; color: #1a1406; }}
.movie .info {{ flex: 1; min-width: 0; }}
.movie .title {{ color: {TEXT}; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.movie .meta {{ color: {MUTED}; font-size: .8rem; }}
.movie .score {{ text-align: right; }}
.movie .score .v {{ font-size: 1.25rem; font-weight: 700; color: {TEXT}; }}
.movie .score .v span {{ color: {GOLD_UI}; font-size: .95rem; }}
.legend-note {{ color: {TEXT_2}; font-size: .86rem; margin-top: 4px; }}
.legend-note .sw {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%;
  background: {GOLD_UI}; margin: 0 6px 0 2px; vertical-align: 0; }}
</style>
""", unsafe_allow_html=True)


# --- Helpers ----------------------------------------------------------------
def styled(chart, height):
    return (chart.properties(height=height, background="transparent")
            .configure_view(stroke=None)
            .configure_axis(labelColor=TEXT_2, titleColor=MUTED, gridColor=GRID,
                            domainColor=AXIS, tickColor=AXIS, labelFont=FONT,
                            titleFont=FONT, labelFontSize=12, titleFontSize=12,
                            titleFontWeight="normal", labelPadding=6)
            .configure_legend(labelColor=TEXT_2, titleColor=TEXT_2, labelFont=FONT,
                              labelFontSize=12, orient="top", symbolSize=110)
            .configure_text(font=FONT))


def show(chart, height):
    st.altair_chart(styled(chart, height), theme=None, width="stretch")


def qhead(anchor, tag, title, sub):
    st.markdown(f'<div class="qhead" id="{anchor}"><span class="tag">{tag}</span>'
                f"<h2>{title}</h2><p>{sub}</p></div>", unsafe_allow_html=True)


def answer(html):
    st.markdown(f'<div class="answer">{html}</div>', unsafe_allow_html=True)


def nice_title(raw):
    """'Close Shave, A (1995)' -> ('A Close Shave', '1995')."""
    m = re.match(r"^(.*?)(?:\s*\((\d{4})\))?\s*$", raw)
    name, year = m.group(1), m.group(2) or ""
    art = re.match(r"^(.*), (The|A|An)$", name)
    return (f"{art.group(2)} {art.group(1)}" if art else name), year


# --- Hero -------------------------------------------------------------------
st.markdown(f"""
<div class="hero">
  <div class="eyebrow">MovieLens 100k · rated 1997–98</div>
  <div class="title">What <span>movie fans</span> really think</div>
  <p>Four questions about 100,000 ratings: which genres show up most, which genres people
  like best, how ratings change with release year, and which movies are truly the best.</p>
</div>
<div class="kpis">
  <div class="kpi"><div class="label">Ratings</div><div class="value">{len(a.df):,}</div></div>
  <div class="kpi"><div class="label">Movies</div><div class="value">{a.df.movie_id.nunique():,}</div></div>
  <div class="kpi"><div class="label">Users</div><div class="value">{a.df.user_id.nunique():,}</div></div>
  <div class="kpi"><div class="label">Average rating</div>
    <div class="value">{a.OVERALL_MEAN:.2f} <span class="star">★</span></div></div>
</div>
<div class="nav">
  <a href="#genres">1 · Genre breakdown</a>
  <a href="#satisfaction">2 · Genre satisfaction</a>
  <a href="#over-time">3 · Ratings over time</a>
  <a href="#best">4 · Best movies</a>
</div>
""", unsafe_allow_html=True)


# --- Q1: Genre breakdown ----------------------------------------------------
qhead("genres", "QUESTION 1", "Genre breakdown",
      "How common is each genre among the 1,682 rated movies?")

n_movies = len(a.movies)
counts = a.movie_genres.genre.value_counts().rename_axis("genre").reset_index(name="movies")
counts["share"] = counts.movies / n_movies
counts["label"] = counts.apply(lambda r: f"{r.movies}  ·  {r.share:.0%}", axis=1)
per_movie = ((a.movies.genres.str.count(r"\|") + 1).value_counts().sort_index()
             .rename_axis("genres").reset_index(name="movies"))
multi_share = per_movie.loc[per_movie.genres > 1, "movies"].sum() / n_movies

left, right = st.columns([1.75, 1], gap="large")
with left:
    base = alt.Chart(counts).encode(
        y=alt.Y("genre:N", sort="-x", title=None, axis=alt.Axis(ticks=False, domain=False)),
        x=alt.X("movies:Q", title="Movies tagged with genre", scale=alt.Scale(domain=[0, 860]),
                  axis=alt.Axis(tickCount=5)),
        tooltip=[alt.Tooltip("genre:N", title="Genre"), alt.Tooltip("movies:Q", title="Movies"),
                 alt.Tooltip("share:Q", title="Share of movies", format=".1%")],
    )
    bars = base.mark_bar(color=BLUE, cornerRadiusEnd=4, height=15)
    labels = base.mark_text(align="left", dx=6, color=TEXT_2, fontSize=11).encode(text="label:N")
    show(bars + labels, 470)
with right:
    st.markdown(f'<div style="margin-top:18px" class="big">{multi_share:.0%}</div>'
                '<div class="bigcap">of movies have more than one genre</div>',
                unsafe_allow_html=True)
    col = alt.Chart(per_movie).encode(
        x=alt.X("genres:O", title="Genres per movie", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("movies:Q", title=None, axis=alt.Axis(tickCount=4)),
        tooltip=[alt.Tooltip("genres:O", title="Genres"), alt.Tooltip("movies:Q", title="Movies")],
    )
    show(col.mark_bar(color=BLUE, cornerRadiusEnd=4, width=26)
         + col.mark_text(dy=-8, color=TEXT_2, fontSize=11).encode(text="movies:Q"), 300)

answer("<b>How I handled multiple genres:</b> each genre string (e.g. "
       "<code>Crime|Film-Noir|Mystery|Thriller</code>) is split on <code>|</code> and the "
       "movie counts <b>once in every genre it has</b>. So shares add up to more than 100%. "
       "The 2 movies tagged only <code>unknown</code> are left out.<br>"
       "<b>Drama</b> (725 movies, 43%) and <b>Comedy</b> (505, 30%) dominate. "
       "Fantasy (22) and Film-Noir (24) are the rarest.")


# --- Q2: Genre satisfaction -------------------------------------------------
qhead("satisfaction", "QUESTION 2", "Genre satisfaction",
      "Which genres get the highest and lowest average ratings?")

g = a.genre_stats().reset_index()
g["lo"], g["hi"] = g["mean"] - g.ci, g["mean"] + g.ci
g["group"] = "Other"
g.loc[g.index[-3:], "group"] = "Top 3"
g.loc[g.index[:3], "group"] = "Bottom 3"

left, right = st.columns([1.75, 1], gap="large")
with left:
    y = alt.Y("genre:N", sort=alt.SortField("mean", order="descending"), title=None,
              axis=alt.Axis(ticks=False, domain=False))
    tip = [alt.Tooltip("genre:N", title="Genre"), alt.Tooltip("mean:Q", title="Mean", format=".2f"),
           alt.Tooltip("n:Q", title="Ratings", format=","),
           alt.Tooltip("ci:Q", title="95% CI ±", format=".3f")]
    xs = alt.Scale(domain=[3.1, 4.05], zero=False)
    ci = alt.Chart(g).mark_rule(color=AXIS, strokeWidth=3, strokeCap="round").encode(
        y=y, x=alt.X("lo:Q", scale=xs, title="Mean rating (★)"), x2="hi:Q")
    dots = alt.Chart(g).mark_circle(size=150, opacity=1, stroke=SURFACE, strokeWidth=2).encode(
        y=y, x=alt.X("mean:Q", scale=xs), tooltip=tip,
        color=alt.Color("group:N", title=None,
                        scale=alt.Scale(domain=["Top 3", "Bottom 3", "Other"],
                                        range=[GOLD, BLUE, SLATE])))
    vals = alt.Chart(g).mark_text(align="left", dx=8, color=TEXT_2, fontSize=11).encode(
        y=y, x=alt.X("hi:Q", scale=xs), text=alt.Text("mean:Q", format=".2f"))
    avg = alt.Chart(pd.DataFrame({"x": [a.OVERALL_MEAN]})).mark_rule(
        color=MUTED, strokeDash=[3, 3]).encode(x=alt.X("x:Q", scale=xs))
    show(avg + ci + dots + vals, 500)
with right:
    def rows(sub, color):
        return "".join(
            f'<div class="rank-row"><span class="dot" style="background:{color}"></span>'
            f'<span class="name">{r.genre}</span><span class="val">{r["mean"]:.2f} ★</span>'
            f'<span class="n">{r.n:,.0f} ratings</span></div>' for _, r in sub.iterrows())
    st.markdown(
        f'<div style="margin-top:22px"><div class="bigcap" style="margin-bottom:8px">Highest rated</div>'
        f'<div class="rank-list">{rows(g.iloc[::-1].head(3), GOLD)}</div>'
        f'<div class="bigcap" style="margin:18px 0 8px">Lowest rated</div>'
        f'<div class="rank-list">{rows(g.head(3), BLUE)}</div>'
        f'<div class="bigcap" style="margin-top:18px">Dashed line = all ratings '
        f'({a.OVERALL_MEAN:.2f}). Grey bars = 95% confidence interval.</div></div>',
        unsafe_allow_html=True)

answer("Every rating counts toward each of its movie's genres. <span class='best'>Film-Noir</span> (3.92) and "
       "<span class='best'>War</span> (3.82) lead; <b>Fantasy</b> (3.22) and <b>Horror</b> (3.29) trail. "
       "Small genres like Documentary have wide intervals, so their exact rank is less certain.")


# --- Q3: Ratings over release year ------------------------------------------
qhead("over-time", "QUESTION 3", "Ratings over time",
      "How does the average rating change with a movie's release year?")

min_n = st.slider("Treat a release year as noisy (hollow dot) when it has fewer than this many ratings",
                  10, 200, 50, step=10)
yearly = (a.df.dropna(subset=["year"]).groupby("year").rating
          .agg(mean="mean", n="count").reset_index())
yearly["reliability"] = (yearly.n >= min_n).map({True: f"≥{min_n} ratings",
                                                 False: f"<{min_n} ratings (noisy)"})
decade = (a.df.dropna(subset=["decade"]).groupby("decade").rating.mean()
          .rename("mean").reset_index())
decade["end"] = decade.decade + 9.6
decade["label"] = decade.decade.astype(int).astype(str) + "s"

xs = alt.Scale(domain=[1920, 2000])
xa = alt.Axis(format="d", tickCount=9)
ys = alt.Scale(domain=[2.9, 4.5], zero=False)
dec = alt.Chart(decade).mark_rule(color=GOLD, strokeWidth=3, opacity=.8, strokeCap="round").encode(
    x=alt.X("decade:Q", scale=xs, axis=xa, title=None), x2="end:Q", y=alt.Y("mean:Q", scale=ys),
    tooltip=[alt.Tooltip("label:N", title="Decade"),
             alt.Tooltip("mean:Q", title="Decade mean", format=".2f")])
pts = alt.Chart(yearly).mark_point(size=60, strokeWidth=1.6).encode(
    x=alt.X("year:Q", scale=xs, axis=xa),
    y=alt.Y("mean:Q", scale=ys, title="Mean rating (★)"),
    color=alt.value(BLUE),
    fill=alt.Fill("reliability:N", title=None,
                  scale=alt.Scale(domain=[f"≥{min_n} ratings", f"<{min_n} ratings (noisy)"],
                                  range=[BLUE, SURFACE])),
    tooltip=[alt.Tooltip("year:Q", title="Release year", format="d"),
             alt.Tooltip("mean:Q", title="Mean", format=".2f"),
             alt.Tooltip("n:Q", title="Ratings", format=",")])
avg = alt.Chart(pd.DataFrame({"y": [a.OVERALL_MEAN]})).mark_rule(
    color=MUTED, strokeDash=[3, 3]).encode(y=alt.Y("y:Q", scale=ys))
show(avg + dec + pts, 380)
st.markdown('<div class="legend-note"><span class="sw"></span>Gold bars = decade average · '
            "dashed line = all ratings · hover any dot for details</div>", unsafe_allow_html=True)

vol = alt.Chart(yearly).mark_bar(color=SLATE, cornerRadiusEnd=2, width=5).encode(
    x=alt.X("year:Q", scale=xs, axis=xa, title="Release year"),
    y=alt.Y("n:Q", title="Ratings", axis=alt.Axis(format=",", tickCount=3)),
    tooltip=[alt.Tooltip("year:Q", title="Release year", format="d"),
             alt.Tooltip("n:Q", title="Ratings", format=",")])
show(vol, 150)

answer("<b>Older movies are rated higher.</b> The decade average peaks at <b>4.01 for the "
       "1940s</b>, stays around 3.87–3.94 through the 1970s, then falls to 3.77 (1980s) and "
       "<b>3.39 for the 1990s</b>. This is most likely selection bias: in 1997–98 the old films "
       "people chose to rate were mostly famous classics, while new releases were rated whether "
       "they were good or bad. The bottom chart shows most of the data is 1990s films.")


# --- Q4: Best movies with a floor -------------------------------------------
qhead("best", "QUESTION 4", "Best movies, with a floor",
      "Top 5 by average rating, counting only movies with enough ratings.")

lo_f, hi_f = st.slider("Minimum number of ratings: drag both handles to compare two floors",
                       10, 300, (50, 150), step=10)
if lo_f == hi_f:
    st.warning("Pick two different floors to compare.")
top = {f: a.top_movies(f) for f in (lo_f, hi_f)}
kept = set(top[lo_f].index) & set(top[hi_f].index)


def movie_cards(floor):
    t = top[floor]
    eligible = (a.movie_stats.n >= floor).sum()
    html = (f'<div class="floor-head"><span class="t">At least {floor} ratings</span>'
            f'<span class="s">{eligible:,} movies qualify</span></div>')
    for rank, (mid, r) in enumerate(t.iterrows(), 1):
        name, year = nice_title(r.title)
        cls = "movie keep" if mid in kept else "movie"
        html += (f'<div class="{cls}"><div class="rank">{rank}</div>'
                 f'<div class="info"><div class="title">{name}</div>'
                 f'<div class="meta">{year} · {r.n:,} ratings</div></div>'
                 f'<div class="score"><div class="v">{r["mean"]:.2f} <span>★</span></div></div></div>')
    return html


left, right = st.columns(2, gap="large")
left.markdown(movie_cards(lo_f), unsafe_allow_html=True)
right.markdown(movie_cards(hi_f), unsafe_allow_html=True)
st.markdown(f'<div class="legend-note"><span class="sw"></span>Gold = in the top 5 at both floors '
            f"({len(kept)} of 5). These are the most reliable picks.</div>",
            unsafe_allow_html=True)

if (lo_f, hi_f) == (50, 150):
    answer("<b>Raising the floor from 50 to 150 replaces 3 of the top 5.</b> All three are "
           "Wallace & Gromit titles (A Close Shave, The Wrong Trousers, Best of Aardman). Each "
           "has fewer than 120 ratings, so a small group of devoted fans pushes its average up. "
           "The 150-floor list is made of widely seen films with 200–300 ratings each. "
           "<span class='best'>Schindler's List</span> and <span class='best'>Casablanca</span> make the top 5 at both floors. A higher "
           "floor gives more trustworthy averages but hides well-loved films that fewer people saw.")
else:
    answer(f"Raising the floor from {lo_f} to {hi_f} replaces <b>{5 - len(kept)} of the top 5</b>. "
           "Drag back to 50 and 150 for the full write-up.")
