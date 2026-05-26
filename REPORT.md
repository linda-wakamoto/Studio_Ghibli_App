
# DATA ANALYSIS REPORT

---

## 1. Data Sources

This project uses two primary data sources:

- **TMDB (The Movie Database) API**
  - Provides structured metadata including:
    - Ratings
    - Budget and revenue
    - Genres
    - Cast and crew
    - Production companies
    - Release dates

- **Studio Ghibli API **

---

## 2. Dataset Overview

- Total movies analyzed: 22
- Matched TMDB + Studio Ghibli records after merging

---

## 3. Visualizations

### Rating Distributions
![Rating Distribution](rating_distributions.png)
This side by side bar graph shows how each site mostly rated the same batch of movies/tv shows.

### Most Common Genres
![Top Genres](top_genres.png)
This bar graph shows which genres were the most prevalent in our dataset, with the genres at the top being most prevalent.

### Average Rating by Genre
![Genre Ratings](genre_ratings.png)
This bar graph shows the average rating of movies/tv shows in our dataset divided by the genre.
---

## 4. Genre Insights

Most common genres in the dataset:

Adventure, Fantasy, Animation, Action, Family


---

## 5. Limitations

- Some Ghibli films like Nausicaa are missing in Ghibli dataset, so they are missing in merged dataset
- Only two data sources were used (TMDB and Studio Ghibli).

---

## 6. Future Improvements

- Integrate additional data sources (e.g. Rotten Tomatoes, Metacritic) which allows for web scraping without written consent
- Expand dataset beyond current sample size
- Add sentiment analysis of reviews for deeper insight

---
