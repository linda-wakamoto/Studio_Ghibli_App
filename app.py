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
    "<p style='text-align: center; font-style: italic; color: #6B7A82; font-size: 1.2rem;'>スタジオジブリの作品</p>",
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
    st.caption("Data sources:")
    st.caption("Studio Ghibli API")
    st.caption("The Movie Database")
    st.caption("STUDIO GHIBLI INC")
    st.markdown("---")
    st.caption("Linda Wakamoto")
    st.caption("STATS418")
    st.caption("Spring 2026")


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
    # VIEW SETTINGS
    # -------------------------
    view_type = st.radio(
        "Display Layout",
        ["Slideshow View", "Grid View"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("---")

    total_films = len(df)

    # =========================================================
    # OPTION A: SLIDESHOW VIEW (CAROUSEL)
    # =========================================================
    if view_type == "Slideshow View":
        ITEMS_PER_PAGE = 3
        max_page = (total_films - 1) // ITEMS_PER_PAGE

        # -------------------------
        # 1. NAVIGATION BUTTONS
        # -------------------------
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

        st.write("")

        # -------------------------
        # 2. IMAGE DATA SLICING
        # -------------------------
        start_idx = st.session_state.carousel_page * ITEMS_PER_PAGE
        end_idx = min(start_idx + ITEMS_PER_PAGE, total_films)
        page_df = df.iloc[start_idx:end_idx]

    # =========================================================
    # OPTION B: GRID VIEW (SHOW ALL FILMS)
    # =========================================================
    else:
        page_df = df
        start_idx = 0

    # -------------------------
    # RENDERING THE IMAGE CARDS
    # -------------------------
    GRID_COLUMNS = 4 if view_type == "Grid View" else len(page_df)
    cols = st.columns(GRID_COLUMNS)

    for idx, (_, row) in enumerate(page_df.iterrows()):
        col_target_idx = idx % GRID_COLUMNS if view_type == "Grid View" else idx
        col = cols[col_target_idx]
        global_idx = idx if view_type == "Grid View" else (start_idx + idx)

        with col:
            img_path = os.path.join("data/movie_images", row["title"].replace(" ", "_"), "image.jpg")

            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()

                st.markdown(
                    f"""
                    <div style="text-align: center; width: 100%; margin-top: 15px;">
                        <img src="data:image/jpeg;base64,{encoded}" 
                             style="max-width: 100%; height: 200px; object-fit: contain; border-radius: 8px;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if st.button(row["title"], key=f"grid_btn_{global_idx}", use_container_width=True):
                st.session_state.selected_idx = global_idx
                st.rerun()

    # -------------------------
    # FIXED SHOW DETAILS (Completely unindented & clean string)
    # -------------------------
    st.markdown("<br>", unsafe_allow_html=True)

    selected_row = df.iloc[st.session_state.selected_idx]
    labels_data = selected_row['labels']

    try:
        labels_data = ast.literal_eval(selected_row['labels']) if isinstance(selected_row['labels'], str) else \
        selected_row['labels']
        cleaned_labels = [str(label).strip().replace("_", " ") for label in labels_data if label.strip()]
    except Exception:
        cleaned_labels = []

    labels_string = ", ".join(cleaned_labels)

    # Building the clean template explicitly without indented spaces inside python markdown wrappers
    details_html = (
        f'<div style="padding: 24px; background-color: #FAF9F6; border-radius: 16px; border: 1px solid #E5E4E2; margin-top: 20px;">'
        f'<div style="font-size: 26px; font-weight: bold; color: #4A7c59; margin-bottom: 12px;">🌸 {html.escape(selected_row["title"])}</div>'
        f'<div style="font-size: 16px; font-weight: normal; color: #4A4A4A; line-height: 1.6; margin-bottom: 20px;">{html.escape(selected_row["description"])}</div>'
        f'<div style="font-size: 16px; font-weight: normal; margin-bottom: 8px;">⭐ <span style="font-weight: bold; color: #333;">{selected_row["tmdb_rating"]}</span></div>'
        f'<div style="font-size: 16px; font-weight: bold; color: #4A7c59;">🏷️ <span style="font-weight: normal; color: #555;">{html.escape(labels_string)}</span></div>'
        f'</div>'
    )

    st.markdown(details_html, unsafe_allow_html=True)
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