# Ghibli Data Analysis Pipeline (TMDB + Ghibli)

---

## Assignment Overview and Goals

This project builds an end-to-end data pipeline to collect, clean, merge, and analyze movie data from two sources:

- TMDB (The Movie Database API)
- Ghibli (Studio Ghibli API)

The goal is to:
- Build a reproducible data pipeline with visual outputs

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
pip install pandas numpy matplotlib seaborn requests beautifulsoup4
```

#### API Keys
---

## This project uses the TMDB API

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

### Step 2: Merge and clean data
```bash
python merge_tmdb_ghibli.py
```
This generates:

data/processed/ghibli_tmdb_merged.csv  
data/processed/ghibli_tmdb_merged.json  

---

### Step 3: Run analysis
```bash
python analyze_data.py
```
Outputs:
- REPORT.md
- .png visualizations

---

## Dependencies

### Python
- pandas
- numpy
- matplotlib
- seaborn
- requests
- beautifulsoup4
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

## Ethical Considerations

- TMDB API used under official terms
- Letterboxd scraping includes 2-second delay between requests
- Data used only for academic purposes
- No personal user data collected
- Robots.txt checked before scraping

---

## Known Limitations

- Some movies have missing ratings/fan counts (e.g. "Balls Up")
- Budget/revenue may be 0 for TV content
- Only two data sources used
- Letterboxd scraping depends on site structure

---

## Future Improvements

- Add data from Rotten Tomatoes or other movie/tv show data sources
- Expand dataset size
- Improve scraping reliability
- Add sentiment analysis

---

## Outputs

### Processed Data
- processed_movies.csv
- processed_movies.json

### Visualizations
- tmdb_vs_letterboxd.png
- rating_distributions.png
- top_genres.png
- genre_ratings.png

### Report
- REPORT.md
