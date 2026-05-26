# streamlit run app.py in terminal

import streamlit as st
import pandas as pd
import os
import ast
import html

from model import predict_films

CSV_PATH = "data/processed/ghibli_interest_labels.csv"
df = pd.read_csv(CSV_PATH)

st.set_page_config(page_title="Ghibli Film Recommender", layout="wide")

st.title("Ghibli Film Explorer")

# =========================
# MODE SELECT
# =========================
mode = st.sidebar.radio(
    "Choose mode",
    ["Image Select", "Label Select"]
)

# =========================================================
# IMAGE MODE (GRID BELOW DETAILS - FIXED SINGLE CLICK)
# =========================================================
if mode == "Image Select":

    # -------------------------
    # INIT STATE
    # -------------------------
    if "selected_idx" not in st.session_state:
        st.session_state.selected_idx = 0

    # -------------------------
    # SHOW DETAILS (TOP)
    # -------------------------
    selected_row = df.iloc[st.session_state.selected_idx]

    st.markdown(
        f"""
        <div style="font-size:25px; font-weight:bold;">
            {selected_row["title"]}
        </div>
        
        <div style="font-size:16px; font-weight:normal;  margin-top:8px;">    
            {selected_row["description"]} 
        </div>
            
        <div style="font-size:18px; font-weight:normal;  margin-top:8px; color:#D4A520;">
            ⭐ Rating: {selected_row['tmdb_rating']}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -------------------------
    # IMAGE GRID (BOTTOM)
    # -------------------------
    st.subheader("Select a film")

    cols = st.columns(3)

    for i, row in df.iterrows():

        col = cols[i % 3]

        with col:

            img_path = os.path.join(
                "data/movie_images",
                row["title"].replace(" ", "_"),
                "image.jpg"
            )

            # show image if exists
            if row["title"] != "Grave of the Fireflies" and os.path.exists(img_path):
                st.image(img_path, width=300)

            # SINGLE CLICK SELECT (FIXED)
            if st.button(row["title"], key=f"btn_{i}"):

                st.session_state.selected_idx = i
                st.rerun()

# =====================================================
# LABEL MODE (RANDOM FOREST)
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

        return sorted(set(v.strip().lower() for v in values))

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

        st.markdown("## Recommended Films")

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
            score = round(pred_row["score"] * 100, 1)

            st.markdown(
                (
                    '<div style="padding:20px;border-radius:10px;">'
                    f'<div style="font-size:26px;font-weight:bold;">{result["title"]}</div>'
                    f'<div style="font-size:16px;margin-top:10px;">{result["description"]}</div>'
                    f'<div style="font-size:20px;color:#D4A520;margin-top:10px;">⭐ Rating: {result["tmdb_rating"]}</div>'
                    f'<div style="font-size:16px;color:#58BF70;margin-top:10px;">'
                    f'Match Confidence: {round(pred_row["score"] * 100, 1)}%'
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