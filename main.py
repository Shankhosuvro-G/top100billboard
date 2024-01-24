from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import gradio as gr
from datetime import datetime

def create_spotify_playlist(date):
    # Convert the input date format to YYYY-MM-DD
    try:
        date_object = datetime.strptime(date, '%d/%m/%Y')
        formatted_date = date_object.strftime('%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Please use dd/mm/yyyy."

    response = requests.get("https://www.billboard.com/charts/hot-100/" + formatted_date)
    soup = BeautifulSoup(response.text, 'html.parser')
    song_names_spans = soup.select("li ul li h3")
    song_names = [song.getText().strip() for song in song_names_spans]

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-modify-private",
            redirect_uri="https://shankhosuvro-g.github.io/misc/",
            client_id="Your Client Id",
            client_secret="Your Client Secret",
            show_dialog=True,
            cache_path="token.txt"
        )
    )
    user_id = sp.current_user()["id"]

    song_uris = []
    year = formatted_date.split("-")[0]
    for song in song_names:
        result = sp.search(q=f"track:{song} year:{year}", type="track")
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} doesn't exist in Spotify. Skipped.")

    playlist = sp.user_playlist_create(user=user_id, name=f"{formatted_date} Billboard 100", public=False)
    sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

    return f"The playlist for {formatted_date} Billboard 100 has been created on Spotify."

# Function to handle button click
def on_submit(date_input):
    result = create_spotify_playlist(date_input)
    return result

# Create a Gradio interface with a submit button
iface = gr.Interface(fn = on_submit, 
                     inputs=gr.Textbox(label='Enter Date in the format of dd/mm/yyyy'), 
                     outputs=gr.Textbox(label='Confirmation'), description="Interface",
                     title="Create Spotify Playlist",
                     thumbnail="spotify_logo.png",
                     theme=gr.themes.Default(primary_hue=gr.themes.colors.red, secondary_hue=gr.themes.colors.pink))
iface.launch(share=True)
