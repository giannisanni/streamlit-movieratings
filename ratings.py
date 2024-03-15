import streamlit as st
from streamlit_gsheets import GSheetsConnection
from PyMovieDb import IMDB
import json
import pandas as pd
import urllib.parse
import re  # Import regular expressions
from PIL import Image

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
        # First, search for the movie to get basic info
        search_results = imdb.search(title)
        if isinstance(search_results, str):
            search_results = json.loads(search_results)
        if not isinstance(search_results, dict):
            return {"error": "Response from search is not in expected dictionary format."}

        search_result_count = search_results.get("result_count", 0)
        search_results_list = search_results.get("results", [])
        if search_result_count > 0 and search_results_list:
            first_search_result = search_results_list[0]
            # Use get_by_name for more detailed information including the description
            detailed_result = imdb.get_by_name(title, tv=False)
            if isinstance(detailed_result, str):
                detailed_result = json.loads(detailed_result)
            if not isinstance(detailed_result, dict):
                return {"error": "Response from get_by_name is not in expected dictionary format."}

            # Extract year, title, and cast from the search result
            match = re.search(r'\b(\d{4})\b', first_search_result.get('name', ''))
            year = match.group(1) if match else None
            parts = first_search_result.get('name', '').split(str(year))
            title = parts[0].strip() if parts else 'N/A'
            cast = parts[1].strip() if len(parts) > 1 else 'N/A'

            # Return combined info
            return {
                "name": title,
                "year": year,
                "cast": cast,
                "url": first_search_result.get('url', 'N/A'),
                "poster": first_search_result.get('poster', 'N/A'),
                "description": detailed_result.get('description', 'N/A')  # Description from detailed result
            }
        else:
            return {"error": "No results found or results list is empty."}
    except Exception as e:
        return {"error": f"Error fetching IMDb info: {e}"}
def main():
    st.sidebar.header("Navigation")

    #page = st.sidebar.radio("Choose an option", ["Movie Ratings Leaderboard", "Select User"])

    if  "Movie Ratings Leaderboard":
        # Sidebar search functionality for the Movie Ratings Leaderboard
        search_query = st.sidebar.text_input("Enter movie name", "")

        st.markdown("""
            <h1 style='text-align: center;'>
                <a href="https://docs.google.com/spreadsheets/d/1qcncR1z4-GCXEVGFpOD-Sq0SFhf72JGvwJ6OMIWBhM8/edit#gid=0" target="_blank">InVivid Movie Ratings Leaderboard</a>
            </h1>
            <br>
        """, unsafe_allow_html=True)

        df = load_movie_ratings()

        # Filter the dataframe based on the search query
        if search_query:
            df = df[df['Films van hoog naar laag beoordeeld'].str.contains(search_query, case=False, na=False)]
        df = df.dropna(subset=['Films van hoog naar laag beoordeeld', 'Rating'])
        # Load and display an image in the sidebar
        image_path = 'invivid.jpg'  # Path to your local image file
        image = Image.open(image_path)
        st.sidebar.image(image, caption='InVivid', use_column_width=True)

        if not df.empty:
            with st.container():
                for index, row in df.iterrows():
                    film = row['Films van hoog naar laag beoordeeld']
                    rating = row['Rating']
                    formatted_rating = f"{rating:.2f}"
                    color = get_color(rating)

                    if index < 3:
                        ranking_display = ["🏆", "🥈", "🥉"][index]
                    elif index < 20:
                        ranking_display = f"{index + 1}. 🌟"
                    else:
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
                                # Display the name, year, and cast
                                st.write(f"**{movie_info.get('name', 'N/A')}** ({movie_info.get('year', 'N/A')})")
                                st.write(f"Cast: {movie_info.get('cast', 'N/A')}")
                                st.write(f"Description: {movie_info.get('description', 'N/A')}")
                                # Normalize the movie name and generate the movie link URL
                                movie_name_normalized = urllib.parse.quote(
                                    movie_info.get('name').lower().replace(" ", "-"))
                                release_year = movie_info.get('year', '')
                                movie_link_url = f"https://en.yts-official.org/movies/{movie_name_normalized}-{release_year}" if release_year else f"https://en.yts-official.org/movies/{movie_name_normalized}"

                                # Use markdown to display IMDb and Watch Movie links side by side
                                links_markdown = f"[IMDb URL]({movie_info.get('url', 'N/A')}) ‧ [Watch Movie]({movie_link_url})"
                                st.markdown(links_markdown, unsafe_allow_html=True)

                            with col1:
                                st.image(movie_info.get('poster', ''), width=100)
                        else:
                            st.error(movie_info["error"])


if __name__ == "__main__":
    main()







