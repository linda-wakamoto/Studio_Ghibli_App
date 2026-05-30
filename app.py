# streamlit run app.py in terminal

import streamlit as st
import pandas as pd
import os
import ast
import html
import base64

from model import predict_films

CSV_PATH = "data/processed/ghibli_interest_labels.csv"
df = pd.read_csv(CSV_PATH)

st.set_page_config(page_title="Ghibli Film Recommender", layout="wide")

# --- App Header ---
st.markdown(
    "<h1 style='text-align: center; color: #4A7c59; font-family: sans-serif;'>🌿 Ghibli Film Explorer 🌿</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; font-style: italic; color: #6B7A82; font-size: 1.2rem;'>Discover the magic of Studio Ghibli</p>",
    unsafe_allow_html=True
)
st.markdown("---")

# --- Button Styling ---
st.markdown("""
    <style>
    /* Target all buttons in the app */
    div.stButton > button {
        background-color: #FAF9F6;     /* Warm Cream */
        color: #4A7c59;                /* Forest Green text */
        border: 2px solid #4A7c59;     /* Forest Green border */
        border-radius: 20px;           /* Rounded pill shape */
        padding: 6px 20px;
        font-weight: 600;
        transition: all 0.3s ease;     /* Smooth transition animation */
    }

    /* Bouncy hover effect */
    div.stButton > button:hover {
        background-color: #4A7c59;     /* Flips to Green background */
        color: #FAF9F6;                /* Flips to Cream text */
        transform: translateY(-2px);   /* Tiny lift up */
        box-shadow: 0px 4px 10px rgba(74, 124, 89, 0.2); /* Soft green glow */
    }

    /* Active/click effect */
    div.stButton > button:active {
        transform: translateY(0px);    /* Pushes back down when clicked */
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# MODE SELECT
# =========================
with st.sidebar:
    st.title("Settings")
    mode = st.radio("Choose mode", ["Image Select", "Label Select"])

    st.markdown("---")
    st.caption("Data source: Studio Ghibli API & Local Metadata")

# =========================================================
# IMAGE MODE
# =========================================================
if mode == "Image Select":

    # -------------------------
    # INIT STATE
    # -------------------------
    if "selected_idx" not in st.session_state:
        st.session_state.selected_idx = 0

    if "carousel_page" not in st.session_state:
        st.session_state.carousel_page = 0

    # -------------------------
    # IMAGE GALLERY (SLIDESHOW)
    # -------------------------
    ITEMS_PER_PAGE = 3
    total_films = len(df)
    max_page = (total_films - 1) // ITEMS_PER_PAGE

    # Control Buttons (Prev / Next Row)
    btn_col1, space_col, btn_col2 = st.columns([1, 6, 1])

    with btn_col1:
        if st.button("← Back", use_container_width=True):
            if st.session_state.carousel_page > 0:
                st.session_state.carousel_page -= 1
                st.rerun()

    with btn_col2:
        if st.button("Next →", use_container_width=True):
            if st.session_state.carousel_page < max_page:
                st.session_state.carousel_page += 1
                st.rerun()

    start_idx = st.session_state.carousel_page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_films)
    page_df = df.iloc[start_idx:end_idx]

    # Render the current slide items horizontally
    # Dynamic columns matching the current page's item count prevents spacing stretching
    cols = st.columns(len(page_df))

    for idx, (_, row) in enumerate(page_df.iterrows()):
        col = cols[idx]
        global_idx = start_idx + idx  # Track true index in original dataframe

        with col:
            img_path = os.path.join("data/movie_images", row["title"].replace(" ", "_"), "image.jpg")

            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()

                # Render fixed smaller height cards to ensure they sit on one screen page
                st.markdown(
                    f"""
                    <div style="text-align: center; width: 100%;">
                        <img src="data:image/jpeg;base64,{encoded}" 
                             style="max-width: 100%; height: 240px; object-fit: contain; border-radius: 8px;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if st.button(row["title"], key=f"grid_btn_{global_idx}", use_container_width=True):
                st.session_state.selected_idx = global_idx
                st.rerun()

    # -------------------------
    # SHOW DETAILS
    # -------------------------
    selected_row = df.iloc[st.session_state.selected_idx]

    labels_data = selected_row['labels']

    try:
        labels_data = ast.literal_eval(selected_row['labels']) if isinstance(selected_row['labels'], str) else \
        selected_row['labels']

        cleaned_labels = [str(label).strip().replace("_", " ") for label in labels_data if label.strip()]
    except Exception:
        cleaned_labels = []

    labels_string = ", ".join(cleaned_labels)

    st.markdown(
        f"""
        <div style="font-size:25px; font-weight:bold; color:#4A7c59; margin-top:20px;">
            🌸 {selected_row["title"]}
        </div>
        
        <div style="font-size:16px; font-weight:normal; margin-top:8px;">    
            {selected_row["description"]} 
        </div>
            
        <div style="font-size:16px; font-weight:normal;  margin-top:32px;">
            ⭐ <span style ="">{selected_row['tmdb_rating']}</span>
        </div>
        
        <div style="font-size:16px; font-weight:bold; margin-top:8px;">
            🏷️ <span style="font-weight:normal;">{labels_string}</span>
        </div>           
        </div>       
        """,
        unsafe_allow_html=True
    )

    st.divider()

# =====================================================
# LABEL MODE (MODELING)
# =====================================================
if mode == "Label Select":

    st.subheader("Choose Your Interests")

    # =========================
    # GET ALL FEATURES
    # =========================
    def parse_list_column(column_name):

        values = []

        for item in df[column_name]:

            try:
                parsed = ast.literal_eval(item)

                if isinstance(parsed, list):
                    values.extend(parsed)

            except:
                pass

        return sorted(set(str(v).strip().replace("_", " ") for v in values))

    all_genres = parse_list_column("genres")
    all_labels = parse_list_column("labels")
    all_species = parse_list_column("species")

    # =========================
    # USER INPUTS
    # =========================
    selected_genres = st.multiselect(
        "Genres",
        all_genres
    )

    selected_labels = st.multiselect(
        "Labels",
        all_labels
    )

    selected_species = st.multiselect(
        "Species",
        all_species
    )

    # =========================
    # COMBINE FEATURES
    # =========================
    selected_features = (
        selected_genres +
        selected_labels +
        selected_species
    )

    # =========================
    # PREDICTIONS
    # =========================
    if selected_features:

        results = predict_films(
            selected_features,
            top_k=5
        )

        st.subheader("Recommended Films")

        for _, pred_row in results.iterrows():

            film_match = df[
                df["title"] == pred_row["title"]
            ]

            if film_match.empty:
                continue

            film_match = df[df["title"] == pred_row["title"]]

            if film_match.empty:
                continue

            result = film_match.iloc[0]

            title = html.escape(result["title"])
            desc = html.escape(result["description"])
            rating = result["tmdb_rating"]

            st.markdown(
                (
                    '<div style="padding:20px;border-radius:10px;">'
                    f'<div style="font-size:26px;font-weight:bold;color:#4A7c59;">🌸 {result["title"]}</div>'
                    f'<div style="font-size:16px;margin-top:10px;">{result["description"]}</div>'
                    f'<div style="font-size:20px;margin-top:10px;">⭐ {result["tmdb_rating"]}</div>'
                    '</div></div>'
                ),
                unsafe_allow_html=True
            )

            # -------------------------
            # IMAGE
            # -------------------------
            folder_name = result["title"].replace(" ", "_")

            img_path = os.path.join(
                "data/movie_images",
                folder_name,
                "image.jpg"
            )

            if os.path.exists(img_path):
                st.image(img_path, width=260)