import json
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
import os

import os

output_dir = ""
os.makedirs(output_dir, exist_ok=True)

# =====================================================
# LOAD PROCESSED DATA
# =====================================================
DATA_PATH = "../data/processed/ghibli_tmdb_merged.csv"

df = pd.read_csv(DATA_PATH)

print(f"Loaded dataset: {len(df)} rows")


# =====================================================
# CLEAN RATINGS
# =====================================================
df["tmdb_rating"] = pd.to_numeric(df["tmdb_rating"], errors="coerce")

# WORD CLOUD
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import re
import matplotlib.pyplot as plt

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# Use existing df (DO NOT reload CSV again)
if "description" not in df.columns:
    raise ValueError("CSV must contain a 'description' column")

text = " ".join(df["description"].dropna().astype(str))

text = text.lower()
text = re.sub(r"[^a-z\s]", " ", text)

words = text.split()

custom_stopwords = {
    "film", "story", "world", "young", "life", "must", "one"
}

filtered_words = [
    w for w in words
    if w not in stop_words
    and w not in custom_stopwords
    and len(w) > 2
]

clean_text = " ".join(filtered_words)

# If text is empty → this prevents silent failure
if len(clean_text.strip()) == 0:
    raise ValueError("WordCloud input text is empty")

wordcloud = WordCloud(
    width=1200,
    height=700,
    background_color="white",
    colormap="viridis",
    max_words=200
).generate(clean_text)

plt.figure(figsize=(14, 8))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Studio Ghibli Word Cloud")

# SAVE CORRECT FILE NAME
plt.savefig(os.path.join(output_dir, "wordcloud.png"), dpi=300, bbox_inches="tight")

plt.close()

# =====================================================
# RATING DISTRIBUTIONS
# =====================================================
plt.figure(figsize=(10, 4))

ratings = df["tmdb_rating"].dropna()

mean_val = ratings.mean()
median_val = ratings.median()
std_val = ratings.std()
min_val = ratings.min()
max_val = ratings.max()

sns.histplot(ratings, bins=20, kde=True)

plt.axvline(mean_val, color='red', linestyle='--', label=f"Mean: {mean_val:.2f}")
plt.axvline(median_val, color='green', linestyle='-', label=f"Median: {median_val:.2f}")

plt.title("TMDB Ratings of Ghibli Movies")

plt.legend()

# Add text box with stats
plt.text(
    0.95, 0.95,
    f"Min: {min_val:.1f}\nMax: {max_val:.1f}\nStd: {std_val:.2f}",
    transform=plt.gca().transAxes,
    verticalalignment='top',
    horizontalalignment='right',
    bbox=dict(boxstyle="round", alpha=0.3)
)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "rating_distributions.png"))
plt.close()


# =====================================================
# GENRE ANALYSIS
# =====================================================
def parse_genres(x):
    if pd.isna(x):
        return []
    if isinstance(x, str):
        return x.replace("[", "").replace("]", "").replace("'", "").split(", ")
    return []


all_genres = []

for g in df["genres"].dropna():
    all_genres.extend(parse_genres(g))

genre_counts = Counter(all_genres)
top_genres = genre_counts.most_common(10)

if top_genres:
    genres, counts = zip(*top_genres)

    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=list(counts), y=list(genres))
    plt.title("Top Genres")

    # Annotate bars
    for i, v in enumerate(counts):
        ax.text(v + 0.2, i, str(v), va='center')

    plt.savefig(os.path.join(output_dir, "top_genres.png"))
    plt.close()


# =====================================================
# AVERAGE RATING BY GENRE
# =====================================================
genre_rows = []

for _, row in df.iterrows():
    genres = parse_genres(row.get("genres"))

    for g in genres:
        genre_rows.append({
            "genre": g.strip(),
            "rating": row["tmdb_rating"]
        })

genre_df = pd.DataFrame(genre_rows)

if not genre_df.empty:
    genre_avg = (
        genre_df.groupby("genre")["rating"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(12, 7))
    ax = genre_avg.plot(kind="bar", width=0.5)
    ax.set_ylim(0,10)
    ax.set_xlabel("Genre", fontsize=12)

    plt.title("Average TMDB Rating by Genre for Ghibli movies", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=13)  # make genre slanted so they're readable

    # Add labels
    for i, v in enumerate(genre_avg):
        ax.text(i, v + 0.05, f"{v:.2f}", ha='center', fontsize=13)

    plt.subplots_adjust(bottom=0.3)  # <-- key fix
    plt.tight_layout()

    plt.savefig(os.path.join(output_dir, "genre_ratings.png"))
    plt.close()

# =====================================================
# MOVIES VS REVENUE
# =====================================================
# Sort by revenue
# ---------------------------
# Clean data (remove budget = 0)
# ---------------------------
revenue_df = df.copy()
revenue_df = revenue_df[
    (revenue_df["budget"].notna()) &
    (revenue_df["budget"] > 0) &
    (revenue_df["revenue"].notna())
]

revenue_df = revenue_df.sort_values(by="revenue", ascending=False)

# ---------------------------
# Plot
# ---------------------------
palette_dict = {
    "Spirited Away": "#FFA500",
    "Howl's Moving Castle": "#4CAF50"
}

# Default to green for everything else
palette = {title: palette_dict.get(title, "#CBCBCB") for title in revenue_df["title"]}

plt.figure(figsize=(14, 7))
ax = sns.barplot(data=revenue_df, x="title", y="revenue", hue = 'title', palette=palette, legend=False)

plt.xticks(rotation=45, ha='right')
ax.set_xlabel("Movie Title", fontsize=12)
ax.set_ylabel("Revenue", fontsize=12)
plt.title("Ghibli Movies by Revenue")

# ---------------------------
# Add value labels
# ---------------------------
for i, v in enumerate(revenue_df["revenue"]):
    ax.text(i, v, f"{v:,.0f}", ha='center', va='bottom', fontsize=8)

plt.subplots_adjust(bottom=0.3)
plt.tight_layout()

plt.savefig(os.path.join(output_dir, "revenue_by_movie.png"))
plt.close()
# =====================================================
# TIMELINE (RELEASE_DATE VS MOVIES)
# =====================================================

df_sorted = df.sort_values(by="release_date").reset_index(drop=True)

plt.figure(figsize=(12, 6))

plt.plot(df_sorted["release_date"], range(len(df_sorted)), marker='o')

# Label each point with movie title
for i, row in df_sorted.iterrows():
    plt.text(row["release_date"], i, row["title"], fontsize=8)

plt.xlabel("Release Date", fontsize=12)
plt.ylabel("Movie Timeline Index", fontsize=12)
plt.title("Ghibli Movie Timeline")

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "timeline.png"))
plt.close()

# =====================================================
# BUDGET BY MOVIE
# =====================================================

# ---------------------------
# Clean data
# ---------------------------
budget_df = df.copy()
budget_df = budget_df[budget_df["budget"].notna()]
budget_df = budget_df[budget_df["budget"] > 0]

budget_df = budget_df.sort_values(by="budget", ascending=False)

# ---------------------------
# Plot
# ---------------------------
plt.figure(figsize=(14, 7))
ax = sns.barplot(data=budget_df, x="title", y="budget", hue = 'title', palette=palette, legend=False)

plt.xticks(rotation=45, ha='right')
ax.set_xlabel("Movie Title", fontsize=12)
ax.set_ylabel("Budget", fontsize=12)
plt.title("Ghibli Movies by Budget")

# ---------------------------
# Add value labels (on top of bars)
# ---------------------------
for i, v in enumerate(budget_df["budget"]):
    ax.text(i, v, f"{v:,.0f}", ha='center', va='bottom', fontsize=8)

plt.subplots_adjust(bottom=0.3)
plt.tight_layout()

plt.savefig(os.path.join(output_dir, "budget_by_movie.png"))
plt.close()

# =====================================================
# FILMS WITH CATS
# =====================================================


# ---------------------------
# Helper: parse species column
# ---------------------------
def parse_species(x):
    if pd.isna(x):
        return []
    if isinstance(x, str):
        return x.replace("[", "").replace("]", "").replace("'", "").split(", ")
    return []

# ---------------------------
# Create "has_cat" column
# ---------------------------
df["has_cat"] = df["species"].apply(lambda x: "Cat" in parse_species(x))

# ---------------------------
# Count values
# ---------------------------
counts = df["has_cat"].value_counts()

labels = ["No Cat", "Cat"]
values = [counts.get(False, 0), counts.get(True, 0)]

# ---------------------------
# Plot
# ---------------------------
plt.figure(figsize=(6, 4))
ax = sns.barplot(x=labels, y=values)

ax.set_xlabel("Category", fontsize=12)
ax.set_ylabel("Number of Films", fontsize=12)
plt.title("Ghibli Films Featuring Cats")

# Add value labels
for i, v in enumerate(values):
    ax.text(i, v, str(v), ha='center', va='bottom')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "cat_films.png"))
plt.close()

# # =====================================================
# # ANALYSIS REPORT
# # =====================================================
#
# top_genres_list = list(genre_counts.keys())[:5]
# top_genres_clean = ", ".join(top_genres_list)
#
# report = f"""
# # DATA ANALYSIS REPORT
#
# ---
#
# ## 1. Data Sources
#
# This project uses two primary data sources:
#
# - **TMDB (The Movie Database) API**
#   - Provides structured metadata including:
#     - Ratings
#     - Budget and revenue
#     - Genres
#     - Cast and crew
#     - Production companies
#     - Release dates
#
# - **Studio Ghibli API **
#
# ---
#
# ## 2. Dataset Overview
#
# - Total movies analyzed: {len(df)}
# - Matched TMDB + Studio Ghibli records after merging
#
# ---
#
# ## 3. Visualizations
#
# ### Rating Distributions
# ![Rating Distribution](rating_distributions.png)
# This side by side bar graph shows how each site mostly rated the same batch of movies/tv shows.
#
# ### Most Common Genres
# ![Top Genres](top_genres.png)
# This bar graph shows which genres were the most prevalent in our dataset, with the genres at the top being most prevalent.
#
# ### Average Rating by Genre
# ![Genre Ratings](genre_ratings.png)
# This bar graph shows the average rating of movies/tv shows in our dataset divided by the genre.
# ---
#
# ## 4. Genre Insights
#
# Most common genres in the dataset:
#
# {top_genres_clean}
#
#
# ---
#
# ## 5. Limitations
#
# - Some Ghibli films like Nausicaa are missing in Ghibli dataset, so they are missing in merged dataset
# - Only two data sources were used (TMDB and Studio Ghibli).
#
# ---
#
# ## 6. Future Improvements
#
# - Integrate additional data sources (e.g. Rotten Tomatoes, Metacritic) which allows for web scraping without written consent
# - Expand dataset beyond current sample size
# - Add sentiment analysis_tmdb_ghibli of reviews for deeper insight
#
# ---
# """
#
# with open("REPORT.md", "w", encoding="utf-8") as f:
#     f.write(report)
#
# print("Analysis complete → REPORT.md saved")