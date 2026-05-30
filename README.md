# Ghibli Data Analysis and Recommendation Pipeline 

---

## Assignment Overview and Goals

This project builds an end-to-end data pipeline to collect, clean, merge, and analyze movie data from four sources,
and produces a machine-learning-powered recommendation application:

- The Movie Database (TMDB) API
- Studio Ghibli API
- Manual Interest Labels
- Ghibli Landscape Images

The goal is to:
- Build a reproducible data pipeline with visual outputs
- Create a content-based recommendation model using Jaccard Similarity
- Deploy an interactive Streamlit application for users to explore the films visually and get recommendations

---

## Setup Instructions

### 1. Clone project
```bash
git clone <repo_url>
cd project
```

### 2. Create virtual environment
```bash
python -m venv venv
```

Activate:

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install requirements.txt
```
---

## API Keys

### Set your API key:

**Mac/Linux**
```bash
export TMDB_API_KEY="your_key_here"
```

**Windows**
```bash
set TMDB_API_KEY=your_key_here
```
---

## How to Run the Pipeline

### Step 1: Collect data (TMDB + GHIBLI APIs)
```bash
python ghibli_api_collector.py
python build_ghibli_entities.py
python tmdb_api_collector.py
```
This generates:

data/processed/ghibli_entities.csv  

---

### Step 2: Extract, clean, and merge data
```bash
python data_processors/build_ghibli_entities.py
python data_processors/merge_tmdb_ghibli.py
python data_processors/ghibli_image_matcher.py
python data_processors/ghibli_label_tagging.py
```
This sanitizes movie titles (lowercase, normalization), fixes rating data types, appends official landscape image links and manual interest tags, and saves the cleaned dataset to data/processed/.

---

### Step 3: Run analysis
```bash
python analysis_tmdb_ghibli/analyze_data.py
```
Outputs:
- Visualization plots saved directly into analysis_tmdb_ghibli/

---

### Step 4: Train, evaluate, and serialize the model
```bash
python model.py
```
This script acts as the machine learning engine:
- Compiles and formats feature vectors into a consolidated token mapping array.
- Validates the system architecture by executing an automated user-profile simulator.
- Quantifies accuracy via Information Retrieval metrics (Hit Rate @ 5 and Mean Reciprocal Rank).
- Runs a Monte Carlo simulation over 1,000 random user queries to test system matrix sparsity.
- Saves the resulting dual-panel diagnostic visualization to jaccard_score_distribution.png and saves the serialized matrices into models/.

---

### Step 5: Launch the web application
```bash
streamlit run app.py
```

## Dependencies

### Python
- streamlit
- pandas
- numpy
- matplotlib
- seaborn
- requests
- python-dotenv
- scikit-learn
- wordcloud
- joblib
---

## Data Sources

### TMDB API
Provides:
- Movie ratings
- Budget and revenue
- Genres
- Cast and crew
- Release dates

---

### Ghibli API

Provides:
- Director
- Producer
- Description
- People
- Locations
- Species
- Vehicles

---

### Manual & Official Assets
Provides:
- Thematic Interest Labels (manually tagged for the recommendation engine)
- Landscape Images (sourced from Studio Ghibli's official website), saved in data/movie_images 

---

## Ethical Considerations

- TMDB API used under official terms
- Studio Ghibli official landscape images are used in compliance with public availability
- Grave of the Fireflies landscape images are omitted out of respect for Studio Ghibli's explicit decision not to disclose or distribute free promotional screenshot assets for that specific film.
- Data used only for academic purposes
- No personal user data collected 

---

## Known Limitations

- Budget and revenue figures for older films or minor co-productions can be incomplete or recorded as 0 in TMDB.
- Recommendation accuracy is tied strictly to the breadth of the manual interest tags and available API metadata.
- Landscape exploration features exactly 22 films due to the asset restrictions surrounding Grave of the Fireflies.

---

## Future Improvements

- Incorporate deeper NLP processing on film descriptions instead of exact match keyword vectors.
- Implement collaborative filtering if user rating datasets become available.

---

## Outputs

### Processed Data 
- data/processed/
  - ghibli_entities.csv (full ghibli csv)
  - ghibli_interest_labels.csv (merged dataset and the labels and images - used for app and modeling)
  - ghibli_tmdb_merged.csv, ghibli_tmdb_merged.json (basic merged dataset without labels and images)

### Models
- data/models
  - feature_encoder.pkl
  - film_model.pkl
  - label_binarizer.pkl
  
### Visualizations

- jaccard_score_distribution.png (Dual-panel distribution modeling global matrix sparsity vs. active top-K return scores)
- analysis_tmdb_ghibli/
  - wordcloud.png (Main themes: human/family, nature, find)
  - rating_distributions.png (Showing right-skewed satisfaction; median 7.79, mean 7.64)
  - top_genres.png (Dominant tags: Animation, Fantasy, Family)
  - genre_ratings.png 
  - budget_by_movie.png 
  - revenue_by_movie.png (Revealing Spirited Away as the peak revenue generator with a remarkably efficient budget)
  - timeline.png 
  - cat_films.png


