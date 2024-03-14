import streamlit as st
from streamlit_gsheets import GSheetsConnection
from PyMovieDb import IMDB
import json
import pandas as pd


st.set_page_config(page_title="InVivid Movie Ratings Leaderboard", page_icon="💰")

# Initialize 'show_data' in session state if it's not already present
if 'show_data' not in st.session_state:
    st.session_state['show_data'] = False

def load_movie_ratings():
    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Read the data from the spreadsheet
    df = conn.read(worksheet="Ranglijst", ttl=0)
    return df

def get_color(rating):
    # Map the rating to a specific color
    if rating >= 9:
        color = "#00FF00"  # Green
    elif rating >= 8:
        color = "#FFD700"  # Yellow
    elif rating >= 6.5:
        color = "#FFA500"  # Orange
    else:
        color = "#FF0000"  # Red
    return color

def fetch_imdb_info(title):
    imdb = IMDB()
    try:
        results = imdb.search(title)
        # Attempt to parse if results is a string (assuming JSON)
        if isinstance(results, str):
            try:
                results = json.loads(results)
            except json.JSONDecodeError:
                return {"error": "Unable to parse response as JSON."}

        if not isinstance(results, dict):
            return {"error": "Response is not in expected dictionary format."}

        result_count = results.get("result_count", 0)
        search_results = results.get("results", [])

        if result_count > 0 and isinstance(search_results, list) and search_results:
            first_result = search_results[0]
            if isinstance(first_result, dict):
                return {
                    "name": first_result.get('name', 'N/A'),
                    "url": first_result.get('url', 'N/A'),
                    "poster": first_result.get('poster', 'N/A')
                    # Ensure you also fetch 'year' and 'imdb_rating' once they are available
                }
            else:
                return {"error": "First result is not a dictionary."}
        else:
            return {"error": "No results found or results list is empty."}
    except Exception as e:
        return {"error": f"Error fetching IMDb info: {e}"}

def main():
    st.title("InVivid Movie Ratings Leaderboard")

    with st.container():
        df = load_movie_ratings()
        # Filter out rows where either 'Films van hoog naar laag beoordeeld' or 'Rating' is nan
        df = df.dropna(subset=['Films van hoog naar laag beoordeeld', 'Rating'])

        if not df.empty:
            emojis = ["🏆", "🥈", "🥉"] + ["🌟"] * 17

            for index, row in df.iterrows():
                film = row['Films van hoog naar laag beoordeeld']
                rating = row['Rating']
                # Format the rating to display with two decimal places
                formatted_rating = f"{rating:.2f}"
                color = get_color(rating)
                emoji = emojis[index] if index < 20 else ""  # Adjust to limit emojis to top 20

                col1, col2 = st.columns([0.1, 1], gap="small")
                with col1:
                    imdb_button = st.button("🔍", key=f"imdb_{index}")
                with col2:
                    st.markdown(f"{emoji} **{film}** with a rating of <span style='color: {color};'>{formatted_rating}</span>", unsafe_allow_html=True)

                if imdb_button:
                    movie_info = fetch_imdb_info(film)
                    if "error" not in movie_info:
                        # Display movie name, year, IMDb rating, IMDb link, and poster
                        # Adjust for 'year' and 'imdb_rating' once they are correctly fetched
                        st.write(f"**{movie_info.get('name', 'N/A')}**")
                        st.markdown(f"[IMDb URL]({movie_info.get('url', 'N/A')})", unsafe_allow_html=True)
                        st.image(movie_info.get('poster', ''), width=100)
                    else:
                        st.error(movie_info["error"])

        else:
            st.write("DataFrame is empty.")


if __name__ == "__main__":
    main()


