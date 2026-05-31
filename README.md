# Studio Ghibli Movie Recommender System & Data Pipeline

---

## Assignment Overview and Goals

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

## Solution Architecture Diagram

```mermaid
graph TD
    %% 1. Data sources and collection methods
    subgraph "1. Data Sources and Collection Methods"
        A1[Studio Ghibli API] -->|ghibli_api_collector.py| B1[data/raw/ghibli/]
        A2[TMDB API] -->|tmdb_api_collector.py| B2[data/raw/ghibli/tmdb/]
        
        S1[Official Ghibli Website] -->|Scraped/Downloaded| IM[data/movie_images/]
        S2[Manual Asset Uploads] -->|Hand-Curated| IM
    end

    %% 2. Data storage/database
    subgraph "2. Data Storage / Database (Local File Structure)"
        B1 -->|Contains| J1[films.json, locations.json, people.json, species.json, vehicles.json]
        B2 -->|Contains| J2[TMDB .json files]
        
        J1 -->|build_ghibli_entities.py| P1[data/processed/ghibli_entities.csv]
        P1 & J2 -->|Merged| P2[data/processed/ghibli_tmdb_merged.csv]
        
        P2 & IM -->|ghibli_image_matcher.py| P3[ghibli_tmdb_mapped_images.csv]
        P3 -->|ghibli_label_tagging.py| P4[(data/processed/final_dataset.csv)]
    end

    %% 3. Model training pipeline
    subgraph "3. Model Training Pipeline"
        P4 -->|train.py| M1[models/film_model.pkl]
        P4 -->|train.py| R1[jaccard_report.png]
        M1 -->|generate_report.py| R2[Performance Report Metrics]
    end

    %% 4 & 5 & 6. Model API Service, Web App Interface, and Deployment Infrastructure
    subgraph "6. Deployment Infrastructure (Cloud Run via CI/CD)"
        CB_ENG[Docker / Podman Build Engine]
        M1 & REQ_API[requirements_api.txt] & DF_API[api/Dockerfile] & M_PY[api/model.py] -->|Compile| CB_ENG
        REQ_APP[requirements_app.txt] & DF_APP[Dockerfile.app] & REQ_GLOBAL[requirements.txt] -->|Compile| CB_ENG
        
        CB_ENG -->|cloudbuild.yaml| AR[Google Artifact Registry]
        
        subgraph "4. Model API Service"
            AR -->|Deploy Container| D1[FastAPI Service on Cloud Run]
        end
        
        subgraph "5. Web Application Interface"
            AR -->|Deploy Container| UI[Streamlit Web App]
        end
    end

    %% 7. How components communicate with each other
    subgraph "7. How Components Communicate (API Calls & Data Flow)"
        D1 ---->|HTTP GET Requests / JSON Payload| UI
        UI ---->|User Interaction| User[End User]
    end

    %% Styling
    style P4 fill:#2cf,stroke:#333,stroke-width:2px
    style M1 fill:#f96,stroke:#333,stroke-width:2px
```
### Diagram Overview

```mermaid

flowchart LR

subgraph S1["1. Data Collection"]
    A["Ghibli API"]
    B["TMDB API"]
    C["Movie Images"]
end

subgraph S2["2. Data Processing"]
    D["Clean & Merge Data"]
    E["Image Matching & Labeling"]
end

subgraph S3["3. Dataset Creation"]
    F[("Final Dataset")]
end

subgraph S4["4. Model Training"]
    G["Train Recommendation Model"]
    H["Serialized Model (.pkl)"]
end

subgraph S5["5. Deployment & Usage"]
    I["FastAPI Service"]
    J["Streamlit Web App"]
    K["End User"]
end

A --> D
B --> D
C --> E

D --> E
E --> F

F --> G
G --> H

H --> I
I --> J
J --> K

style F fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
style H fill:#e1f5fe,stroke:#01579b,stroke-width:2px
style J fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

## Technology Stack & Tools Used
* **Frontend Interface:** Streamlit (Custom Themed Layout)
* **Backend Framework:** FastAPI / Uvicorn
* **Containerization:** Docker & Google Cloud Artifact Registry
* **Cloud Orchestration:** Google Cloud Build (`cloudbuild.yaml`)
* **Production Hosting:** Google Cloud Run (Serverless Environment)

## Deployment Links
- **Interactive Streamlit Web Application:** [Live App Link](https://app-service-750112593840.us-central1.run.app/)
- **Model Inference API Endpoint:** [Live API Link](https://api-service-750112593840.us-central1.run.app/docs)
(features: type in the labels, species, genres, and top_k: type in the number of movie recommendations you would like)

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

### 3. Install dependencies
```bash
pip install -r requirements_app.txt
pip install -r requirements_api.txt
pip install -r requirements.txt
```
---

## API Keys

### Set your API key:

**Windows**
```bash
set TMDB_API_KEY=your_key_here
```
---

## How to Run the Pipeline

### Step 1: Collect data (TMDB + GHIBLI APIs)
```bash
python data_collectors/ghibli_api_collector.py
python data_processors/build_ghibli_entities.py
python data_collectors/tmdb_api_collector.py
```
This generates:

data/processed/ghibli_entities.csv  

The two api collectors contain logging for the data collection process, and adds both ghibli and tmdb api use in the logs folder as "api_collector.log".
These collectors and build_ghibli_entities also have tests that can be run using:

```bash
python -m pytest
```

---

### Step 2: Extract, clean, and merge data
```bash
python data_processors/merge_tmdb_ghibli.py
python data_processors/ghibli_image_matcher.py
python data_processors/ghibli_label_tagging.py
```
This sanitizes movie titles (lowercase, normalization), fixes rating data types, appends official landscape image links and manual interest tags, and saves the cleaned dataset to data/processed/.
The final processed dataset is final_dataset.csv, and has data from all four sources.

These data processors also have tests that can be run using:
```bash
python -m pytest
```

---

### Step 3: Run analysis on final dataset
```bash
python analysis/analyze_data.py
```
Outputs:
- Visualization plots saved directly into analysis/
- Findings are written in REPORT.md from the generate_report.py script
---

### Step 4: Train, evaluate, and serialize the model
```bash
python train.py
```
This script acts as the primary data science engine of our machine learning pipeline:
- **Matrix Engineering:** Extracts and flattens array tokens from categorical vectors (genres, labels, species) using safe ast.literal_eval parsing routines to combine multi-source features into unified content-profile mappings.
- **Deterministic Serialization:** Maps individual film titles directly to token footprint dictionaries and locks down the training state by saving the finalized, lightweight mathematical token layout directly to models/film_model.pkl.
- **Sparsity & Evaluation Simulation:** Executes a localized Monte Carlo Simulation over 1,000 randomized user profile request arrays. It stress-tests system matrix density limits, checks global similarity overlaps, and computes empirical performance metrics across top-K target windows.
- **Diagnostic Visualization:** Automatically outputs a dual-panel analysis matrix saved directly to jaccard_report.png, displaying the historical mathematical distribution metrics for global data sparsity versus active matching scores.

---

### Step 5: Launch the web application
```bash
streamlit run app.py
```

---

### Step 6: Containerization

How to run this on Podman (PowerShell)
1. Initialize the Network Environment

Create the dedicated network bridge so the services can discover each other:

```powershell
podman network create ghibli-network
```

2. Build and launch the FastAPI image

```powershell
podman build -t ghibli-api -f api/Dockerfile .

podman run -d `
  --name api-service `
  --network ghibli-network `
  -p 8080:8080 `
  localhost/ghibli-api
```

3. Build and Launch the Frontend App

Build the Streamlit image
```powershell
podman build -t ghibli-app -f Dockerfile.app .
```

Run the container
```powershell
podman run -d `
  --name app-service `
  --network ghibli-network `
  -p 8501:8501 `
  -e API_URL="http://api-service:8080/recommend" `
  localhost/ghibli-app
```
Local Access Verification: 

Once running (podman ps), open your browser to http://localhost:8501 for the user interface, or http://localhost:8080/docs for the interactive Swagger API documentation.

---

### Step 7: Continuous Cloud Deployment

The cloud infrastructure is pushed using the Google Cloud SDK CLI toolchain:

Submit Backend Image: 

```powershell
gcloud builds submit --tag us-central1-docker.pkg.dev/[PROJECT_ID]/ghibli-repo/api-service:v1 api/
```

Submit Frontend Image: 

```powershell
gcloud builds submit --config=cloudbuild.yaml .
```

Deploy Web Routing: 

Executed via Serverless Google Cloud Run deployment commands with dynamic environment variable cross-linking to connect the UI frontend securely to the hosted API core.

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
- nltk
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
- Grave of the Fireflies landscape images are omitted out of respect for Studio Ghibli's explicit decision not to disclose or distribute free promotional screenshot assets for that specific film
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

## Outputs

### Processed Data 
- data/processed/
  - ghibli_entities.csv (full ghibli csv)
  - ghibli_tmdb_merged.csv, ghibli_tmdb_merged.json (basic merged dataset without labels and images)
  - final_dataset.csv (merged dataset and the labels and images - used for app and modeling)

### Models
- models/
  - film_model.pkl
  
### Visualizations

- jaccard_report.png (Dual-panel distribution modeling global matrix sparsity vs. active top-K return scores for the prediction model)

- analysis_tmdb_ghibli/
  - wordcloud.png 
  - rating_distributions.png 
  - top_genres.png 
  - genre_ratings.png 
  - budget_by_movie.png 
  - revenue_by_movie.png 
  - timeline.png 
  - top_labels.png 
  - label_ratings.png 
  - species_distribution.png 
  - genre_label_species_correlation.png

### AI Assistant Documentation

For my project, I used ChatGPT and Google Gemini chatbots to share my code and receive feedback.
Helpful prompts included describing what I wanted from the model and app, and giving a lot of information, such as:

"I want to find common traits of Ghibli movies.
I want labels that matches movies to interests - like:
Racoons: Pom Poko
Cats: My Neighbor Totoro, The Cat Returns, Whisper of the Heart
Witch: Kiki’s Delivery Service, Howl’s Moving Castle, Earwig and the Witch, Spirited Away..."

AI helped me with the architecture of my model and app, while I had to manually edit the code so that 
it handles messy data issues such as lowercase or uppercase titles, title aliases, and null values.

I learned that Google Gemini is very useful in looking at tabs and pdf and pictures of my project, 
and providing code to make my final app UI visually pleasing. I learned about adding emojis and color to my streamlit app
that I wouldn't have known without these tools. However, I had to make sure that their solutions matched my real data, and debug any issues that arose.


