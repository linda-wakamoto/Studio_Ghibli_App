import os
from pathlib import Path
from datetime import datetime

# =========================================================
# ABSOLUTE PROJECT ROOT (ANCHOR THIS FILE)
# =========================================================
BASE_DIR = Path(__file__).resolve().parent

# go up until you hit STATS418_Project
# (this avoids PyCharm / pytest / docker issues)
while BASE_DIR.name != "STATS418_Project":
    BASE_DIR = BASE_DIR.parent

PROJECT_ROOT = BASE_DIR

print("PROJECT_ROOT:", PROJECT_ROOT)

# =========================================================
# OUTPUT PATH
# =========================================================
OUTPUT_PATH = PROJECT_ROOT / "report.md"

print("OUTPUT_PATH:", OUTPUT_PATH)

# =========================================================
# FIGURES
# =========================================================
FIG_DIR = PROJECT_ROOT / "analysis"

def fig(name):
    return f"analysis/{name}"

def fig_api(name):
    return name

figures = {
    "wordcloud": fig("wordcloud.png"),
    "ratings": fig("rating_distributions.png"),
    "genres": fig("top_genres.png"),
    "genre_ratings": fig("genre_ratings.png"),
    "labels": fig("top_labels.png"),
    "label_ratings": fig("label_ratings.png"),
    "revenue": fig("revenue_by_movie.png"),
    "budget": fig("budget_by_movie.png"),
    "timeline": fig("timeline.png"),
    "species": fig("species_distribution.png"),
    "correlation": fig("genre_label_species_correlation.png"),
    "model": fig_api("jaccard_report.png")
}

# =========================================================
# REPORT CONTENT
# =========================================================
report = f"""
# Studio Ghibli Data Analysis & Recommendation Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Overview

This project builds an end-to-end data pipeline to collect, clean, merge, and analyze movie data from four sources,
and produces a machine-learning-powered recommendation application for Studio Ghibli Films:

- The Movie Database (TMDB) API
- Studio Ghibli API
- Manual Interest Labels
- Ghibli Landscape Images

The goal is to:
- Build a reproducible data pipeline with visual outputs
- Create a content-based recommendation model using Jaccard Similarity
- Deploy an interactive Streamlit application for users to explore the films visually and get recommendations

---

## Exploratory Data Analysis

### Word Cloud
From the film descriptions, the main themes from studio ghibli movies are related to self and family ("girl", "boy", "human", "family"), nature ("sea", "bamboo", "island"), and discovery ("find", "discover").
![wordcloud]({figures["wordcloud"]})

### Ratings Distribution
Ghibli movies show right-skewed ratings, with a median of 7.79, and mean of 7.64.

![ratings]({figures["ratings"]})

### Genres
The most common genres are Animation, Fantasy, Family.

![genres]({figures["genres"]})

### Genre Ratings
The average ratings were similar across genres, but Action and History had the highest.

![genre_ratings]({figures["genre_ratings"]})

### Labels
The most common labels were "family" and "friendship".

![labels]({figures["labels"]})

### Label Ratings
The average ratings were similar across labels, but "dragons" and "strong lead" had the highest.

![label_ratings]({figures["label_ratings"]})

### Revenue
Spirited Away had the highest revenue, and Howl's Moving Castle came in second.

![revenue]({figures["revenue"]})

### Budget
Tale of the Princess Kaguya had the highest budget, but Howl's Moving Castle and Spirited Away did not - even with the top two highest revenues.
![budget]({figures["budget"]})

### Timeline
The earliest film was Castle in the Sky and the latest in this dataset was Earwig and the Witch.

![timeline]({figures["timeline"]})

### Species
The most common species/characters were humans, then cats, and there were 7 different species in total.

![species]({figures["species"]})

### Correlation Heatmap
This shows a comprehensive correlation analysis on all three features of the model, and the highest correlations were between the History genre and Romance genre, castle label and Action genre, and dragon species and Action genre.

![correlation]({figures["correlation"]})

---

## Recommendation System

I built a content-based recommender using:

- genres
- labels
- species

Similarity metric:
Jaccard similarity:
A ∩ B / A ∪ B

These graphs show results from the Jaccard Similarity Matrix that scores how well the movie matches the user input.

Left: Jaccard Similarity scores for all pairwise movie matches across entire catalog
The spike at 0 shows that most movies have no overlapping genre, labels, species with one another (but the right skew shows there are some).

Right: Scores of top 5 recommendations (how similar are the recommendations)
The bulk of recommended movies have similarity scores between 0.1 and 0.25 - model finds most relevant matching films for user, and finds the small amount of movies that match well.

![model]({figures["model"]})
---

## Model Evaluation

After performing 1,000 Monte Carlo Runs to simulate user input, I found that:
- Global Sparsity: The simulation confirms high feature sparsity across the catalog (a massive spike at 0 similarity), proving our movie metadata is highly distinct and descriptive.
- Top-K Quality: Isolating the top 5 recommendations reveals that the model successfully surfaces the small cluster of highly relevant films.
- Mean Reciprocal Rank (MRR): Achieves a strong MRR of 0.6402, mathematically proving that the most relevant, highest-scoring movies consistently land in the 1st and 2nd spots of the user's grid.

---

## Deployment

FastAPI endpoint:
`/recommend?features=family&features=magic`

Returns ranked film recommendations.

---

## Conclusion

This project demonstrates an end-to-end ML pipeline:
raw APIs → cleaning → feature engineering → EDA → recommender → deployment.

---

## AI Assistant Documentation

For my project, I used ChatGPT and Google Gemini chatbots to share my code and receive feedback.
Helpful prompts included describing what I wanted from the model and app, and give a lot of information, such as:

"I want to find common traits of Ghibli movies.
I want labels that matches movies to interests - like:
Racoons: Pom Poko
Cats: My Neighbor Totoro, The Cat Returns, Whisper of the Heart
Witch: Kiki’s Delivery Service, Howl’s Moving Castle, Earwig and the Witch, Spirited Away..."

AI helped me with the architecture of my model and app, while I had to manually edit the code so that 
it handles messy data issues such as lowercase or uppercase titles, title aliases, and null values.

I learned that Google Gemini is very useful in looking at tabs and pdf and pictures of my project, 
and providing code to make my final app UI visually pleasing. I learned about adding emojis and color to my streamlit app
that I wouldn't have known without these tools. However, I definitely couldn't blindly use all the code they provided,
and had to make sure that their solutions matched my real data, and debug any issues that arose.

---

## Ethical Considerations

- TMDB API used under official terms
- Studio Ghibli official landscape images are used in compliance with public availability
- Grave of the Fireflies landscape images are omitted out of respect for Studio Ghibli's explicit decision not to disclose or distribute free promotional screenshot assets for that specific film.
- Data used only for academic purposes
- No personal user data collected 

---

## Known Limitations

- This dataset does not include the most recent Ghibli Film - The Boy and the Heron (2024), and does not include other well-known films made before Studio Ghibli but directed by Hayao Miyazaki (such as Nausicaa)
- Budget and revenue figures for older films or minor co-productions can be incomplete or recorded as 0 in TMDB.
- People, Locations, Vehicles all had many null values from the Ghibli API.
- Recommendation accuracy is tied strictly to the breadth of the manual interest tags and available API metadata.
- Landscape exploration features do not include Grave of the Fireflies, as the Studio Ghibli official website did not upload pictures available for this film.

---

## Future Improvements

- Incorporate deeper NLP processing on film descriptions instead of exact match keyword vectors.
- Implement collaborative filtering if user rating datasets become available.

---

"""

# =========================================================
# SAVE REPORT
# =========================================================
os.makedirs(PROJECT_ROOT, exist_ok=True)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(report)

print("Report generated at:", OUTPUT_PATH)
