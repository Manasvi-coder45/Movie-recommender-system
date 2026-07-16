import pandas as pd
import streamlit as st
import joblib
import requests

APP_NAME = "Cine Compass"

st.set_page_config(
    page_title=f"{APP_NAME} | Movie Recommender",
    page_icon=":clapper:",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #12141c 0%, #1a1d29 100%);
}
h1 {
    color: #eae6f0;
    font-weight: 800;
    text-align: center;
    letter-spacing: 1px;
    padding-bottom: 0px;
}
.subtitle {
    text-align: center;
    color: #8f95a3;
    margin-top: -8px;
    margin-bottom: 32px;
    font-size: 15px;
}
.movie-card {
    background: #20232f;
    border-radius: 14px;
    padding: 12px;
    text-align: center;
    border: 1px solid #2c2f3d;
    transition: transform 0.2s ease-in-out, border 0.2s ease-in-out;
}
.movie-card:hover {
    transform: translateY(-4px);
    border: 1px solid #7c6ef2;
}
.movie-title {
    color: #eae6f0;
    font-size: 14px;
    font-weight: 600;
    margin-top: 10px;
    min-height: 40px;
}
div.stButton > button {
    background-color: #7c6ef2;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 8px 24px;
    font-weight: 600;
}
div.stButton > button:hover {
    background-color: #6a5cf0;
    color: white;
}
section[data-testid="stSidebar"] {
    background-color: #171a24;
}
</style>
""", unsafe_allow_html=True)

movies = joblib.load("movies_df.joblib")
similarity = joblib.load("similarity.joblib")

TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", None)
PLACEHOLDER_POSTER = "https://via.placeholder.com/300x450.png?text=No+Poster"


@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    """Fetch poster URL from TMDB using the movie_id already present in movies_df."""
    if not TMDB_API_KEY:
        return PLACEHOLDER_POSTER
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return PLACEHOLDER_POSTER
    except Exception:
        return PLACEHOLDER_POSTER


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movies_list:
        row = movies.iloc[i[0]]
        recommended_movies.append(row.title)
        recommended_posters.append(fetch_poster(row.movie_id))

    return recommended_movies, recommended_posters


with st.sidebar:
    st.markdown(f"### {APP_NAME}")
    st.write(
        "Pick a movie you enjoyed and find five others "
        "that share similar themes, genres, and story elements! "
    )
    st.markdown("---")
    st.caption("Spend less time scrolling and more time watching.")

st.title(APP_NAME)
st.markdown('<p class="subtitle">Your compass through the endless sea of movies</p>', unsafe_allow_html=True)

selected_movie_name = st.selectbox(
    "Type or select a movie you enjoyed:",
    movies['title'].values,
    index=None,
    placeholder="Search for a movie..."
)

if st.button("Recommend"):
    if not selected_movie_name:
        st.warning("Please select a movie first.")
    else:
        with st.spinner("Finding movies similar to your taste..."):
            names, posters = recommend(selected_movie_name)

        cols = st.columns(5)
        for col, name, poster in zip(cols, names, posters):
            with col:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                st.image(poster, use_container_width=True)
                st.markdown(f'<div class="movie-title">{name}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)