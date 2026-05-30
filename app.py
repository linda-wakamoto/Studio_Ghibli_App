import streamlit as st
import pandas as pd
import os
import ast
import html
import base64
import requests

# --- API Config ---
API_URL = os.getenv("API_URL", "http://127.0.0.1:8080/recommend")

# --- Dynamic Path Resolution ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "final_dataset.csv")
df = pd.read_csv(CSV_PATH)

st.set_page_config(page_title="Studio Ghibli Film Recommender", layout="wide")

# --- App Header ---
st.markdown(
    "<h1 style='text-align: center; color: #4A7c59; font-family: sans-serif;'>🌿 Studio Ghibli Film Explorer 🌿</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# --- Button & Typography Styling ---
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #FAF9F6;
        color: #4A7c59;
        border: 2px solid #4A7c59;
        border-radius: 20px;
        padding: 6px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #4A7c59;
        color: #FAF9F6;
        transform: translateY(-2px);
        box-shadow: 0px 4px 10px rgba(74, 124, 89, 0.2);
    }
    div.stButton > button:active {
        transform: translateY(0px);
    }
    .stSubheader h3 {
        font-size: 2rem !important;
    }
    div[data-testid="stMultiSelect"] label p {
        font-size: 1.4rem !important;
        font-weight: 500 !important;
        color: #4A7c59 !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR CONFIGURATION
# =========================================================
with st.sidebar:
    st.markdown("<h1 style='font-size: 2rem;'>Settings</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        div[data-testid="stSidebar"] .stRadio p { font-size: 1.25rem !important; }
        div[data-testid="stRadio"] label p { font-size: 1.3rem !important; font-weight: 500; }
        div[data-testid="stRadio"] [data-testid="stWidgetBorderGroup"] { border: none !important; padding: 0 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
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
    if "selected_idx" not in st.session_state:
        st.session_state.selected_idx = 0
    if "carousel_page" not in st.session_state:
        st.session_state.carousel_page = 0

    view_type = st.radio("Display Layout", ["Slideshow View", "Grid View"], horizontal=True,
                         label_visibility="collapsed")
    st.markdown("---")
    total_films = len(df)

    if view_type == "Slideshow View":
        ITEMS_PER_PAGE = 3
        max_page = (total_films - 1) // ITEMS_PER_PAGE
        btn_col1, space_col, btn_col2 = st.columns([1, 6, 1])

        st.markdown(
            """
            <style>
            div.stButton > button p { font-size: 1.25rem !important; font-weight: normal !important; }
            div.stButton > button { padding: 12px 24px !important; height: auto !important; min-height: 4rem !important; }
            </style>
            """,
            unsafe_allow_html=True
        )

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
        start_idx = st.session_state.carousel_page * ITEMS_PER_PAGE
        end_idx = min(start_idx + ITEMS_PER_PAGE, total_films)
        page_df = df.iloc[start_idx:end_idx]
    else:
        page_df = df
        start_idx = 0

    GRID_COLUMNS = 4 if view_type == "Grid View" else len(page_df)
    cols = st.columns(GRID_COLUMNS)

    for idx, (_, row) in enumerate(page_df.iterrows()):
        col_target_idx = idx % GRID_COLUMNS if view_type == "Grid View" else idx
        col = cols[col_target_idx]
        global_idx = idx if view_type == "Grid View" else (start_idx + idx)

        with col:
            # FIX: Lowercase normalization matching your system's path architecture
            clean_folder = row["title"].lower().replace(" ", "_")
            img_path = os.path.join(BASE_DIR, "data", "movie_images", clean_folder, "image.jpg")

            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                st.markdown(
                    f"""
                    <div style="text-align: center; width: 100%; margin-top: 15px; margin-bottom: 20px;">
                        <img src="data:image/jpeg;base64,{encoded}" style="max-width: 100%; height: 200px; object-fit: contain; border-radius: 8px;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            if st.button(row["title"], key=f"grid_btn_{global_idx}", use_container_width=True):
                st.session_state.selected_idx = global_idx
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    selected_row = df.iloc[st.session_state.selected_idx]

    try:
        labels_data = ast.literal_eval(selected_row['labels']) if isinstance(selected_row['labels'], str) else \
        selected_row['labels']
        cleaned_labels = [str(label).strip().replace("_", " ") for label in labels_data if str(label).strip()]
    except Exception:
        cleaned_labels = []

    labels_string = ", ".join(cleaned_labels)

    details_html = (
        f'<div style="padding: 24px; background-color: #FAF9F6; border-radius: 16px; border: 1px solid #E5E4E2; margin-top: 20px;">'
        f'<div style="font-size: 30px; font-weight: bold; color: #4A7c59; margin-bottom: 12px;">🌸 {html.escape(selected_row["title"])}</div>'
        f'<div style="font-size: 20px; font-weight: normal; color: #4A4A4A; line-height: 1.6; margin-bottom: 20px;">{html.escape(selected_row["description"])}</div>'
        f'<div style="font-size: 24px; font-weight: normal; margin-bottom: 8px;">⭐ <span style="font-weight: bold; color: #333;">{selected_row["tmdb_rating"]}</span></div>'
        f'<div style="font-size: 24px; font-weight: bold; color: #4A7c59;">🏷️ <span style="font-weight: normal; color: #555;">{html.escape(labels_string)}</span></div>'
        f'</div>'
    )
    st.markdown(details_html, unsafe_allow_html=True)
    st.divider()

# =========================================================
# LABEL MODE (MODELING INTERFACE)
# =========================================================
if mode == "Label Select":
    st.subheader("Choose Your Interests")


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

    selected_genres = st.multiselect("Genres", all_genres)
    selected_labels = st.multiselect("Labels", all_labels)
    selected_species = st.multiselect("Species", all_species)

    # UI Clean features array
    display_features = selected_genres + selected_labels + selected_species

    # FIX: Re-convert clean UI space strings to data underscores for backend compatibility
    selected_features = [f.replace(" ", "_") for f in display_features]

    if selected_features:
        st.subheader("Recommended Films")

        try:
            response = requests.get(API_URL, params={"features": selected_features, "top_k": 100})

            if response.status_code == 200:
                data = response.json()
                recommendations = data.get("recommendations", [])

                if not recommendations:
                    st.info("No matching films found for the selected criteria.")

                for pred_row in recommendations:
                    film_match = df[df["title"] == pred_row["title"]]
                    if film_match.empty:
                        continue

                    result = film_match.iloc[0]
                    title = html.escape(result["title"])
                    desc = html.escape(result["description"])
                    rating = result["tmdb_rating"]

                    st.markdown(
                        (
                            '<div style="padding:20px; border-radius:10px; margin-bottom:10px; background-color:#FAF9F6; border: 1px solid #E5E4E2;">'
                            f'<div style="font-size:26px; font-weight:bold; color:#4A7c59;">🌸 {title}</div>'
                            f'<div style="font-size:16px; margin-top:10px; color:#4A4A4A;">{desc}</div>'
                            f'<div style="font-size:20px; margin-top:10px;">⭐ {rating}</div>'
                            '</div>'
                        ),
                        unsafe_allow_html=True
                    )

                    # Look inside lowercase paths for matching posters
                    clean_folder_name = result["title"].lower().replace(" ", "_")
                    img_path = os.path.join(BASE_DIR, "data", "movie_images", clean_folder_name, "image.jpg")
                    if os.path.exists(img_path):
                        st.image(img_path, width=260)
                        st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.error(f"Backend API error (Status Code: {response.status_code})")

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the recommendation backend API. Verify the FastAPI service is running.")