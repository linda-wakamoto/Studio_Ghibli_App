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

st.markdown(
    """
    <h1 style="color: #177A1F; font-size: 40px; font-weight: bold; margin-bottom: 24px;">
        🌿 Ghibli Film Explorer 🌿
    </h1>
    """,
    unsafe_allow_html=True
)
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
        <div style="font-size:30px; font-weight:bold; margin-top:20px;">
            {selected_row["title"]}
        </div>
        
        <div style="font-size:18px; font-weight:normal;  margin-top:8px;">    
            {selected_row["description"]} 
        </div>
            
        <div style="font-size:20px; font-weight:normal;  margin-top:32px;">
            ⭐ <span style ="">{selected_row['tmdb_rating']}</span>
        </div>
        
        <div style="font-size:18px; font-weight:bold; margin-top:8px;">
            🏷️ <span style="font-weight:normal;">{labels_string}</span>
        </div>           
        </div>       
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -------------------------
    # IMAGE GRID (BOTTOM)
    # -------------------------
    st.subheader("Select a film")

    # Shift columns back to 3
    cols = st.columns(3)

    for i, row in df.iterrows():

        # Change the modulo to 3 so it alternates perfectly across three columns
        col = cols[i % 3]

        with col:

            img_path = os.path.join(
                "data/movie_images",
                row["title"].replace(" ", "_"),
                "image.jpg"
            )

            # --- show image if exists ---
            if os.path.exists(img_path):
                import base64

                # Convert local image to HTML-friendly data URI
                with open(img_path, "rb") as f:
                    data = f.read()
                    encoded = base64.b64encode(data).decode()

                # NO CROPPING: Fully preserved shapes arranged beautifully in a 3-column grid
                st.markdown(
                    f"""
                        <div style="text-align: center; width: 100%;">
                            <img src="data:image/jpeg;base64,{encoded}" 
                                 style="max-width: 100%; height: 220px; object-fit: contain; border-radius: 12px;">
                        </div>
                        """,
                    unsafe_allow_html=True
                )

                # --- SHOW THE BUTTON (DIRECTLY BELOW THE IMAGE) ---
                if st.button(row["title"], key=f"grid_btn_{i}", use_container_width=True):
                    st.session_state.selected_idx = i
                    st.rerun()

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

            st.markdown(
                (
                    '<div style="padding:20px;border-radius:10px;">'
                    f'<div style="font-size:26px;font-weight:bold;">{result["title"]}</div>'
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