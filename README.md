# CTP Week 4 — Movie Ratings Analysis

An analysis of the [MovieLens 100k](https://grouplens.org/datasets/movielens/100k/) dataset:
100,000 ratings (1–5 stars) from 943 users on 1,682 movies, collected in 1997–98.
It answers four questions with charts, and an interactive Streamlit dashboard presents them.

https://ctpweek4-ckfhenstykjhdqhwchaee4.streamlit.app/

## Questions & findings

### 1. Genre breakdown
**What's the distribution of genres among the rated movies?**

Movies can have several genres (e.g. `Crime|Film-Noir|Mystery|Thriller`). I split the
genre string on `|` and counted each movie **once in every genre it has**, so the
genre shares add up to more than 100%. Half of all movies (50.5%) have more than one genre.

- **Drama** is the most common genre (725 movies, 43%), followed by **Comedy** (505, 30%).
- **Fantasy** (22) and **Film-Noir** (24) are the rarest.

### 2. Genre satisfaction
**Which genres have the highest and lowest average rating?**

Every rating counts toward each of its movie's genres. The average across all ratings is 3.53.

| Highest | Mean | Lowest | Mean |
|---|---|---|---|
| Film-Noir | 3.92 | Fantasy | 3.22 |
| War | 3.82 | Horror | 3.29 |
| Drama | 3.69 | Children | 3.35 |

### 3. Ratings over time
**How has the mean rating changed across movie release years?**

Older movies are rated higher. By decade of release, the average peaks at **4.01 for the
1940s**, stays around 3.87–3.94 through the 1970s, then falls to 3.77 for the 1980s and
**3.39 for the 1990s**. The likely cause is selection bias: in 1997–98, the old films people
chose to rate were mostly famous classics, while new releases were rated whether good or bad.

### 4. Best movies, with a floor
**Top 5 movies by mean rating, counting only movies with at least 50 vs. 150 ratings.**

| # | ≥ 50 ratings | ≥ 150 ratings |
|---|---|---|
| 1 | A Close Shave — 4.49 | Schindler's List — 4.47 |
| 2 | Schindler's List — 4.47 | Casablanca — 4.46 |
| 3 | The Wrong Trousers — 4.47 | The Shawshank Redemption — 4.45 |
| 4 | Casablanca — 4.46 | Rear Window — 4.39 |
| 5 | Wallace & Gromit: Best of Aardman — 4.45 | The Usual Suspects — 4.39 |

Raising the floor to 150 replaces 3 of the top 5. All three are Wallace & Gromit titles
with fewer than 120 ratings each. **Schindler's List** and **Casablanca** make the top 5
at both floors.

![Best movies section](screenshots/dashboard_best_movies.png)

## Running it

```bash
pip install -r requirements.txt

# Interactive dashboard (opens at http://localhost:8501)
streamlit run app.py

# Regenerate the static PNG charts in charts/
python analysis.py
```

On the dashboard, you can change the "noisy year" cutoff in Q3 and drag the two
minimum-ratings floors in Q4 to compare any two floors.

## Project structure

| Path | What it is |
|---|---|
| `movie_ratings.csv` | One row per rating, with user, movie, genre and release-year columns |
| `analysis.py` | Data prep and the four static charts (matplotlib) saved to `charts/` |
| `app.py` | Streamlit dashboard with interactive Altair charts |
| `.streamlit/config.toml` | Dashboard theme (dark slate with gold accent) |
| `charts/` | Static PNG answers to Q1–Q4 |
| `screenshots/` | Dashboard screenshots used in this README |
| `Buildingprocess.txt` | Notes on how the dashboard design evolved |

## Notes on the data

- Movies are grouped by `movie_id`, not title, because 18 titles appear under two different IDs.
- The 2 movies whose only genre is `unknown` are left out of the genre analysis.
- 30 ratings have no release year and are left out of Q3.
