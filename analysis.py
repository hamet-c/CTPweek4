"""Week 4 - MovieLens ratings analysis.

Answers four questions with one chart each (saved to charts/):
  Q1  Genre breakdown           -> charts/q1_genre_breakdown.png
  Q2  Genre satisfaction        -> charts/q2_genre_satisfaction.png
  Q3  Ratings over release year -> charts/q3_ratings_over_time.png
  Q4  Top 5 with a ratings floor -> charts/q4_top_movies_floor.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path(__file__).parent / "movie_ratings.csv"
OUT = Path(__file__).parent / "charts"
OUT.mkdir(exist_ok=True)

# --- Palette & style -------------------------------------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
NEUTRAL = "#b9b8b0"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 10,
    "text.color": INK,
    "axes.labelcolor": INK_2,
    "axes.edgecolor": BASELINE,
    "axes.linewidth": 0.8,
    "axes.titlesize": 12,
    "axes.titleweight": "semibold",
    "axes.titlelocation": "left",
    "axes.titlepad": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK_2,
    "ytick.labelcolor": INK_2,
    "legend.frameon": False,
})


def suptitle(fig, title, subtitle):
    fig.text(0.01, 0.985, title, fontsize=15, fontweight="semibold", va="top")
    fig.text(0.01, 0.935, subtitle, fontsize=10, color=INK_2, va="top")


def save(fig, name):
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved charts/{name}")


# --- Load ------------------------------------------------------------------
df = pd.read_csv(DATA)
OVERALL_MEAN = df.rating.mean()

# One row per movie. Group by movie_id, not title: some titles map to
# more than one movie_id in this dataset.
movies = df.drop_duplicates("movie_id")[["movie_id", "title", "year", "genres"]]

# Multi-genre handling: split "Crime|Film-Noir|Mystery" into a list and
# explode so a movie (or rating) counts once in EACH of its genres.
# Genre shares therefore sum to more than 100%. The 2 "unknown" movies are dropped.
movie_genres = (movies.assign(genre=movies.genres.str.split("|"))
                .explode("genre").query("genre != 'unknown'"))
rating_genres = (df.assign(genre=df.genres.str.split("|"))
                 .explode("genre").query("genre != 'unknown'"))


# --- Q1: Genre breakdown ---------------------------------------------------
def q1():
    n_movies = len(movies)
    by_genre = movie_genres.genre.value_counts().sort_values()
    per_movie = (movies.genres.str.count(r"\|") + 1).value_counts().sort_index()
    multi_share = per_movie[per_movie.index > 1].sum() / n_movies

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 6.6),
                                  gridspec_kw={"width_ratios": [2.2, 1], "wspace": 0.3})
    suptitle(fig, "Q1 · Genre breakdown of the 1,682 rated movies",
             f"{multi_share:.0%} of movies carry more than one genre. Each movie is counted "
             "once in every genre it has, so shares add up to more than 100%.")

    ax.barh(by_genre.index, by_genre.values, height=0.62, color=BLUE)
    for i, (g, v) in enumerate(by_genre.items()):
        ax.text(v + 8, i, f"{v}  ({v / n_movies:.0%})", va="center", fontsize=9, color=INK_2)
    ax.set_title("Movies tagged with each genre")
    ax.set_xlabel("Number of movies")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, by_genre.max() * 1.18)
    ax.tick_params(axis="y", length=0)

    ax2.bar(per_movie.index.astype(str), per_movie.values, width=0.6, color=BLUE)
    for x, v in zip(per_movie.index.astype(str), per_movie.values):
        ax2.text(x, v + 12, f"{v}", ha="center", fontsize=9, color=INK_2)
    ax2.set_title("How many genres does a movie have?")
    ax2.set_xlabel("Genres per movie")
    ax2.set_ylabel("Number of movies")
    ax2.grid(axis="x", visible=False)

    fig.subplots_adjust(top=0.84)
    save(fig, "q1_genre_breakdown.png")

    print(f"  Drama {by_genre['Drama']} ({by_genre['Drama'] / n_movies:.0%}), "
          f"Comedy {by_genre['Comedy']}; multi-genre share {multi_share:.1%}")


# --- Q2: Genre satisfaction ------------------------------------------------
def q2():
    g = (rating_genres.groupby("genre").rating
         .agg(mean="mean", n="count", sd="std").sort_values("mean"))
    g["ci"] = 1.96 * g.sd / np.sqrt(g.n)
    top3, bottom3 = g.index[-3:], g.index[:3]
    colors = [BLUE if x in top3 else ORANGE if x in bottom3 else NEUTRAL for x in g.index]

    fig, ax = plt.subplots(figsize=(11, 7))
    suptitle(fig, "Q2 · Average rating by genre",
             "Every rating counts toward each of its movie's genres. Lines show 95% confidence "
             "intervals; n = ratings in that genre.")

    y = np.arange(len(g))
    ax.hlines(y, g["mean"] - g.ci, g["mean"] + g.ci, color=BASELINE, lw=2)
    ax.scatter(g["mean"], y, s=70, color=colors, edgecolor=SURFACE, linewidth=2, zorder=3)
    ax.axvline(OVERALL_MEAN, color=MUTED, lw=1)
    ax.text(OVERALL_MEAN, len(g) - 0.3, f" all ratings {OVERALL_MEAN:.2f}",
            fontsize=9, color=INK_2, va="bottom")
    for yi, (name, r) in zip(y, g.iterrows()):
        ax.text(r["mean"] + r.ci + 0.012, yi, f"{r['mean']:.2f}   n={r.n:,.0f}",
                va="center", fontsize=9, color=INK_2)
    ax.set_yticks(y, g.index)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(3.0, 4.25)
    ax.set_ylim(-0.7, len(g) + 0.2)
    ax.set_xlabel("Mean rating (1–5 stars)")

    handles = [plt.Line2D([], [], marker="o", ls="", ms=8, color=c, label=l)
               for c, l in [(BLUE, "Top 3"), (ORANGE, "Bottom 3"), (NEUTRAL, "Others")]]
    ax.legend(handles=handles, loc="lower right")

    fig.subplots_adjust(top=0.86)
    save(fig, "q2_genre_satisfaction.png")
    print("  highest:", ", ".join(f"{k} {v:.2f}" for k, v in g["mean"][::-1][:3].items()))
    print("  lowest: ", ", ".join(f"{k} {v:.2f}" for k, v in g["mean"][:3].items()))


# --- Q3: Ratings over release year -----------------------------------------
def q3():
    MIN_N = 50
    yearly = (df.dropna(subset=["year"]).groupby("year").rating
              .agg(mean="mean", n="count"))
    solid = yearly[yearly.n >= MIN_N]
    thin = yearly[yearly.n < MIN_N]
    decade = df.dropna(subset=["decade"]).groupby("decade").rating.mean()

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(13, 7.6), sharex=True,
                                  gridspec_kw={"height_ratios": [2.4, 1], "hspace": 0.12})
    suptitle(fig, "Q3 · Mean rating by movie release year",
             "Older movies rate higher. Ratings fall from about 3.9 for pre-1980 films to about "
             "3.3 for 1996–98 releases. Bottom panel: how many ratings sit behind each year.")

    # Decade mean as a step line behind the yearly dots
    for dec, m in decade.items():
        ax.hlines(m, dec, dec + 9.6, color=BLUE, lw=2, alpha=0.45)
    ax.scatter(solid.index, solid["mean"], s=36, color=BLUE, edgecolor=SURFACE, lw=1.5, zorder=3)
    ax.scatter(thin.index, thin["mean"], s=36, facecolor=SURFACE, edgecolor=BLUE, lw=1.2, zorder=3)
    ax.axhline(OVERALL_MEAN, color=MUTED, lw=1)
    ax.text(1921, OVERALL_MEAN - 0.03, f"all ratings {OVERALL_MEAN:.2f}",
            fontsize=9, color=INK_2, va="top")
    ax.text(1989.4, decade[1990], f"1990s avg {decade[1990]:.2f}",
            fontsize=9, color=INK_2, va="center", ha="right")
    ax.annotate(f"1940s avg {decade[1940]:.2f}", xy=(1944.5, decade[1940]),
                xytext=(1943.5, 4.22), fontsize=9, color=INK_2, va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.set_ylabel("Mean rating")
    ax.set_ylim(2.9, 4.5)
    ax.grid(axis="x", visible=False)
    handles = [
        plt.Line2D([], [], marker="o", ls="", ms=7, color=BLUE, label=f"Year with ≥{MIN_N} ratings"),
        plt.Line2D([], [], marker="o", ls="", ms=7, mfc=SURFACE, mec=BLUE,
                   label=f"Year with <{MIN_N} ratings (noisy)"),
        plt.Line2D([], [], lw=2, color=BLUE, alpha=0.45, label="Decade mean"),
    ]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3,
              borderaxespad=0.2)

    ax2.bar(yearly.index, yearly.n, width=0.75, color=NEUTRAL)
    ax2.set_ylabel("Ratings")
    ax2.set_xlabel("Release year")
    ax2.grid(axis="x", visible=False)
    ax2.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    ax2.text(1996, yearly.n.max(), f"{yearly.loc[1996, 'n']:,} ",
             ha="right", va="top", fontsize=9, color=INK_2)

    fig.subplots_adjust(top=0.84)
    save(fig, "q3_ratings_over_time.png")
    print("  decade means:", ", ".join(f"{int(k)}s {v:.2f}" for k, v in decade.items()))
    print(f"  r(year, mean) over years with >={MIN_N} ratings: "
          f"{np.corrcoef(solid.index, solid['mean'])[0, 1]:.2f}")


# --- Q4: Top 5 with a ratings floor ----------------------------------------
def q4():
    stats = (df.groupby("movie_id")
             .agg(title=("title", "first"), mean=("rating", "mean"), n=("rating", "count")))
    top = {f: stats[stats.n >= f].sort_values("mean", ascending=False).head(5) for f in (50, 150)}
    both = set(top[50].index) & set(top[150].index)

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.2), sharex=True,
                             gridspec_kw={"wspace": 0.75})
    suptitle(fig, "Q4 · Top 5 movies by mean rating, at two minimum-ratings floors",
             "Raising the floor from 50 to 150 ratings swaps out 3 of the top 5. "
             "Blue = in the top 5 at both floors, orange = in the top 5 at this floor only.")

    for ax, floor in zip(axes, (50, 150)):
        t = top[floor].iloc[::-1]
        eligible = (stats.n >= floor).sum()
        colors = [BLUE if mid in both else ORANGE for mid in t.index]
        y = np.arange(len(t))
        ax.hlines(y, 4.0, t["mean"], color=GRID, lw=2)
        ax.scatter(t["mean"], y, s=90, color=colors, edgecolor=SURFACE, lw=2, zorder=3)
        for yi, (_, r) in zip(y, t.iterrows()):
            ax.text(r["mean"] + 0.025, yi, f"{r['mean']:.2f}  (n={r.n})",
                    va="center", fontsize=9, color=INK_2)
        ax.set_yticks(y, t.title)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="y", visible=False)
        ax.set_title(f"Floor: ≥{floor} ratings   ({eligible} movies qualify)")
        ax.set_xlim(4.0, 4.85)
        ax.set_xlabel("Mean rating (axis starts at 4.0)")

    fig.subplots_adjust(top=0.72)
    save(fig, "q4_top_movies_floor.png")
    for f, t in top.items():
        print(f"  floor {f}:")
        for _, r in t.iterrows():
            print(f"    {r['mean']:.3f}  n={r.n:<4} {r.title}")


if __name__ == "__main__":
    for fn in (q1, q2, q3, q4):
        print(fn.__name__.upper())
        fn()
