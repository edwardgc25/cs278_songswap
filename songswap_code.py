# Library imports for retrieving info from website through viewing HTML. 
import requests
from bs4 import BeautifulSoup 
import string
import time

# Library imports for creating playlist using Spotify's API.
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify credentials for API use. 
client_id = '96977a9087564527bf3a53a8025807db'
client_secret = 'f7756c7fcdef423b88e9412e463742ff'
redirect_url = 'https://alicelr5.wixsite.com/songswap'


# This function extracts all posts from the homepage of SongSwap. 
def get_all_song_posts():
    
    #Initializing 
    url = 'https://alicelr5.wixsite.com/songswap'
    song_posts = []

    # Go to website 
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
    
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all posts (hyperlinks) within homepage 
        links = soup.find_all('a')
        
        # Extract where all hyperlinks lead to (href)
        for link in links:
            href = link.get('href')
            if href and href.startswith('https://alicelr5.wixsite.com/songswap/forum/general-discussion/'):
                if len(href.split('/')) == 7:
                    song_posts.append(href)
                    
    return song_posts


# This function retrieves song title and artist from each post found on SongSwap home. 
def retrieve_song_info(song_posts):
    
    songs_info = []
    
    for post in song_posts:
        # Go to url
        url = post
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title_artist_tag = soup.find('h1') # Find all posts with header tag (where song is posted)

            if title_artist_tag:
                title_artist = title_artist_tag.text.strip() # Extract data 
                
                # Split text by hyphen to separate the song title and artist
                parts = title_artist.split('-')
                
                # Make sure post is formatted by title and artist
                if len(parts) >= 2:
                    song_title = ' '.join(parts[:-1]) # Grab first part to get song title
                    song_title = song_title.strip()  # Extract actual title 

                    artist = parts[-1] 
                    artist = artist.strip()  

                    songs_info.append({'title': song_title, 'artist': artist}) # Add to list of songs and format properly
           
           
    print("Song Titles and Artists:")
    for song in songs_info:
        print(f"Title: {song['title']}, Artist: {song['artist']}")

    return songs_info


# This function gets token for making playlist on Spotify API.
def get_spotify_token(client_id, client_secret):
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_url,
                                               scope="playlist-modify-public"))
    
    return sp


# This token takes previously scraped songs in order make playlist on Spotify.
def create_spotify_playlist(sp, songs_info):
    
    # Create a new playlist
    user_id = sp.me()['id']
    playlist_name = 'SongSwap of the Week!'
    playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
    playlist_id = playlist['id']

    # Search for each song on Spotify and add it to the playlist
    for song in songs_info:  
        query = f"track:\"{song['title']}\" artist:\"{song['artist']}\"" # Find song, format for Spotify to find 
        #print(f"Searching for: {query}")
        result = sp.search(query, limit=1, type='track') # Only take top result of search and save it. 
        
        # If track found, obtain id and add to playlist. Sleep to not overload Spotify API. 
        if result['tracks']['items']: 
            track_id = result['tracks']['items'][0]['id']
            sp.user_playlist_add_tracks(user_id, playlist_id, [track_id])
            #print(f"Added: {song['title']} by {song['artist']}")
        time.sleep(1) # Limit number of requests 

    playlist_url = playlist['external_urls']['spotify']
    print(f"Playlist created: {playlist['external_urls']['spotify']}")
    return playlist_url

# This function obtains all of the emails of our users, in order to generate mailing list. 
def retrieve_emails():
    response = requests.get(WIX_API_URL)
    if response.status_code == 200:
        return response.json().get('emails', [])



def main():
    # Retrieve songs.
    song_posts = get_all_song_posts()
    songs_info = retrieve_song_info(song_posts)

    # Make playlist. 
    token = get_spotify_token(client_id, client_secret)
    playlist_url= create_spotify_playlist(token, songs_info)
    

if __name__ == "__main__":
    main()