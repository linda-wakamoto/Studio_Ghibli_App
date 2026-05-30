import pandas as pd
import seaborn as sns
from collections import Counter
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import re
import matplotlib.pyplot as plt
import os

output_dir = "."
os.makedirs(output_dir, exist_ok=True)

# =====================================================
# LOAD PROCESSED DATA
# =====================================================
DATA_PATH = "../data/processed/final_dataset.csv"

df = pd.read_csv(DATA_PATH)

print(f"Loaded dataset: {len(df)} rows")


# =====================================================
# CLEAN RATINGS
# =====================================================
df["tmdb_rating"] = pd.to_numeric(df["tmdb_rating"], errors="coerce")

# WORD CLOUD
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

    plt.subplots_adjust(bottom=0.3)
    plt.tight_layout()

    plt.savefig(os.path.join(output_dir, "genre_ratings.png"))
    plt.close()

# =====================================================
# LABEL ANALYSIS
# =====================================================
def parse_labels(x):
    if pd.isna(x):
        return []
    if isinstance(x, str):
        return x.replace("[", "").replace("]", "").replace("'", "").split(", ")
    return []


all_labels = []

for l in df["labels"].dropna():
    all_labels.extend(parse_labels(l))

label_counts = Counter(all_labels)
top_labels = label_counts.most_common(10)

if top_labels:
    labels, counts = zip(*top_labels)

    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=list(counts), y=list(labels))
    plt.title("Top Labels")

    # Annotate bars
    for i, v in enumerate(counts):
        ax.text(v + 0.2, i, str(v), va='center')

    plt.subplots_adjust(left=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "top_labels.png"))
    plt.close()


# =====================================================
# AVERAGE RATING BY Label
# =====================================================
label_rows = []

for _, row in df.iterrows():
    labels = parse_labels(row.get("labels"))

    for l in labels:
        label_rows.append({
            "labels": l.strip(),
            "rating": row["tmdb_rating"]
        })

label_df = pd.DataFrame(label_rows)

if not label_df.empty:
    label_avg = (
        label_df.groupby("labels")["rating"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(12, 7))
    ax = label_avg.plot(kind="bar", width=0.5)
    ax.set_ylim(0,10)
    ax.set_xlabel("Label", fontsize=12)

    plt.title("Average TMDB Rating by Label for Ghibli movies", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=13)  # make genre slanted so they're readable

    # Add labels
    for i, v in enumerate(label_avg):
        ax.text(i, v + 0.05, f"{v:.2f}", ha='center', fontsize=13)

    plt.subplots_adjust(bottom=0.3)
    plt.tight_layout()

    plt.savefig(os.path.join(output_dir, "label_ratings.png"))
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
# SPECIES DISTRIBUTION
# =====================================================

all_species = []

for s in df["species"].dropna():
    parsed_items = parse_species(s)
    all_species.extend([item.strip() for item in parsed_items if item.strip()])

species_counts = Counter(all_species)
# Sorts the distribution inherently in descending order
top_species = species_counts.most_common()

if top_species:
    species_names, counts = zip(*top_species)

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        x=list(counts),
        y=list(species_names),
        hue=list(species_names),
        palette="viridis",
        legend=False
    )
    plt.title("Distribution of Species in Ghibli Films", fontsize=14)
    plt.xlabel("Count", fontsize=12)
    plt.ylabel("Species", fontsize=12)

    # Annotate bars
    for i, v in enumerate(counts):
        ax.text(v + 0.1, i, str(v), va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "species_distribution.png"), dpi=300)
    plt.close()

# =====================================================
# CORRELATION BETWEEN GENRES, LABELS, AND SPECIES
# =====================================================
# Filter out empty or blank strings ('') from the top 10 species list
top_g = [g for g, c in Counter(all_genres).most_common(10) if g.strip()]
top_l = [l for l, c in Counter(all_labels).most_common(10) if l.strip()]
top_s = [s for s, c in Counter(all_species).most_common(10) if s.strip()]  # FIX: Removes blanks

binary_rows = []
for _, row in df.iterrows():
    m_genres = parse_genres(row.get("genres"))
    m_labels = parse_labels(row.get("labels"))
    m_species = parse_species(row.get("species"))

    feature_dict = {}
    # Build binary indicator mapping (1 if present, 0 if absent)
    for g in top_g:
        feature_dict[f"Genre: {g}"] = 1 if g in m_genres else 0
    for l in top_l:
        feature_dict[f"Label: {l}"] = 1 if l in m_labels else 0
    for s in top_s:
        feature_dict[f"Species: {s}"] = 1 if s in m_species else 0

    binary_rows.append(feature_dict)

corr_df = pd.DataFrame(binary_rows)

if not corr_df.empty:
    # Calculate Pearson correlation matrix across dummy-encoded features
    corr_matrix = corr_df.corr()

    plt.figure(figsize=(16, 14))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8}
    )
    plt.title("Correlation Heatmap between Top Genres, Labels, and Species", fontsize=16, pad=20)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "genre_label_species_correlation.png"), dpi=300)
    plt.close()