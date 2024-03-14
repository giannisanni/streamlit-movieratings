import streamlit as st
from streamlit_gsheets import GSheetsConnection
from PyMovieDb import IMDB
import json
import pandas as pd

st.set_page_config(page_title="InVivid Movie Ratings Leaderboard", page_icon="🎬")

if 'show_data' not in st.session_state:
    st.session_state['show_data'] = False


def load_movie_ratings():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Ranglijst", ttl=0)
    return df


def get_color(rating):
    if rating >= 9:
        color = "#00FF00"
    elif rating >= 8:
        color = "#FFD700"
    elif rating >= 6.5:
        color = "#FFA500"
    else:
        color = "#FF0000"
    return color


def fetch_imdb_info(title):
    imdb = IMDB()
    try:
        results = imdb.search(title)
        if isinstance(results, str):
            results = json.loads(results)
        if not isinstance(results, dict):
            return {"error": "Response is not in expected dictionary format."}
        result_count = results.get("result_count", 0)
        search_results = results.get("results", [])
        if result_count > 0 and search_results:
            first_result = search_results[0]
            return {
                "name": first_result.get('name', 'N/A'),
                "url": first_result.get('url', 'N/A'),
                "poster": first_result.get('poster', 'N/A')
            }
        else:
            return {"error": "No results found or results list is empty."}
    except Exception as e:
        return {"error": f"Error fetching IMDb info: {e}"}


def main():
    #st.title("InVivid Movie Ratings Leaderboard")
    # Use markdown to create a prominently styled link at the top of the page
    st.markdown("""
        <h1 style='text-align: center;'>
            <a href="https://docs.google.com/spreadsheets/d/1qcncR1z4-GCXEVGFpOD-Sq0SFhf72JGvwJ6OMIWBhM8/edit#gid=0" target="_blank">InVivid Movie Ratings Leaderboard</a>
        </h1>
    """, unsafe_allow_html=True)

    with st.container():
        df = load_movie_ratings()
        df = df.dropna(subset=['Films van hoog naar laag beoordeeld', 'Rating'])

        if not df.empty:
            for index, row in df.iterrows():
                film = row['Films van hoog naar laag beoordeeld']
                rating = row['Rating']
                formatted_rating = f"{rating:.2f}"
                color = get_color(rating)

                # Define emoji or ranking display based on index
                if index < 3:  # Top 3 have their own emojis and no number
                    ranking_display = ["🏆", "🥈", "🥉"][index]
                elif index < 10:  # Ranks 4-20 get a star emoji
                    ranking_display = f"{index + 1}. 🌟"
                else:  # Beyond rank 20, just show the number
                    ranking_display = f"{index + 1}."

                col1, col2 = st.columns([1, 0.1], gap="small")
                with col2:
                    imdb_button = st.button("ℹ️", key=f"imdb_{index}")
                with col1:
                    st.markdown(
                        f"{ranking_display} **{film}** with a rating of <span style='color: {color};'>{formatted_rating}</span>",
                        unsafe_allow_html=True)

                if imdb_button:
                    movie_info = fetch_imdb_info(film)
                    if "error" not in movie_info:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            st.write(f"**{movie_info.get('name', 'N/A')}**")
                            st.markdown(f"[IMDb URL]({movie_info.get('url', 'N/A')})", unsafe_allow_html=True)
                        with col1:
                            st.image(movie_info.get('poster', ''), width=100)
                    else:
                        st.error(movie_info["error"])

        else:
            st.write("DataFrame is empty.")


if __name__ == "__main__":
    main()









