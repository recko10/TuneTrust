# importing packages 
from pytube import YouTube 
import os
from bs4 import BeautifulSoup  
import requests
from googleapiclient.discovery import build
import os
from spleeter.separator import Separator
import billboard

###TODO what about features? Filter them out or find a way to extract just the main artist's vocals?

# Spotify API credentials
client_id = '3b64e6bb35194f178259cd780c36b780'
client_secret = 'c19e538aec6b46d79567356396d33bc6'

# YouTube API credentials
api_key = 'AIzaSyAd3S0HLMvGn2qVn8g0Tph5hBrdw55t1ZI'
youtube = build('youtube', 'v3', developerKey=api_key)

# Download vids from YouTube
def download_song(link, artistName):
    # url input from user 
    yt = YouTube( 
        str(link))
    
    try:
        # extract only audio 
        video = yt.streams.filter(only_audio=True).first()
    except KeyError:
        print("Something went wrong! Skipping song")
        return None
    
    # check for destination to save file 
    print("Enter the destination (leave blank for current directory)") 
    destination = str(f"songs/{artistName}") or '.'
    
    # download the file 
    out_file = video.download(output_path=destination) 
    
    # save the file 
    base, ext = os.path.splitext(out_file) 
    new_file = base + '.mp3'
    os.rename(out_file, new_file) 
    
    # result of success 
    print(yt.title + " has been successfully downloaded.")
    return True

# Get an access token
def get_access_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

# Get artist ID by name
def get_artist_id(artist_name, access_token):
    search_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'q': artist_name,
        'type': 'artist',
        'limit': 1
    }
    response = requests.get(search_url, headers=headers, params=params)
    results = response.json()
    artist_id = results['artists']['items'][0]['id']
    return artist_id

# Get all albums
def get_all_albums_by_artist(artist_id, access_token):
    albums = []
    next_url = f'https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album,single&market=US&limit=50'
    headers = {'Authorization': f'Bearer {access_token}'}

    while next_url:
        response = requests.get(next_url, headers=headers)
        data = response.json()
        albums.extend(data['items'])
        next_url = data.get('next')  # Update next_url for the next iteration

    return albums

# Get all songs from albums
def get_all_tracks_from_albums(albums, access_token):
    tracks = []
    headers = {'Authorization': f'Bearer {access_token}'}

    for album in albums:
        album_id = album['id']
        next_url = f'https://api.spotify.com/v1/albums/{album_id}/tracks?market=US&limit=50'

        while next_url:
            response = requests.get(next_url, headers=headers)
            data = response.json()
            tracks.extend([track['name'] for track in data['items']])
            next_url = data.get('next')  # Update next_url for the next iteration

    return tracks

# Fetch all song names from an artist
def get_all_tracks(artist_name):
    access_token = get_access_token(client_id, client_secret)
    artist_id = get_artist_id(artist_name, access_token)
    albums = get_all_albums_by_artist(artist_id, access_token)
    tracks = get_all_tracks_from_albums(albums, access_token)
    return tracks

def search_youtube(query):
    # Search request
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=1,
        type='video'
    ).execute()

    # Extracting video information
    if search_response['items']:
        video_id = search_response['items'][0]['id']['videoId']
        video_title = search_response['items'][0]['snippet']['title']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        return video_url, video_title
    else:
        return None, "No results found"

# Search for song on YT, pick first link, download
def pull_artist(artist_name):
    for song in get_all_tracks(artist_name):
        query = f"{song} by {artist_name}"
        video_url, video_title = search_youtube(query)
        if video_url:
            print(f"Video title: {video_title}")
            print(f"Video URL: {video_url}")
            if download_song(video_url, artist_name):
                print("Download success")
            else:
                print("Download fail")
        else:
            print("Fail: No URL")

def separate_stems(artist_name):
    # Define the path to the directory containing the audio files
    audio_files_directory = f'songs/{artist_name}'

    # Define the output directory where the separated tracks will be saved
    output_directory = f'songs/{artist_name}/stems'

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Initialize the Separator with the desired configuration
    separator = Separator('spleeter:2stems')  # '2stems' model separates vocals and accompaniment

    # Iterate over each file in the directory
    for filename in os.listdir(audio_files_directory):
        if filename.endswith(".mp3") or filename.endswith(".wav"):  # Check file extension
            file_path = os.path.join(audio_files_directory, filename)
            try:
                # Process the file (separate and save the vocals)
                separator.separate_to_file(file_path, output_directory)
                print(f"Processed {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
        else:
            print(f"Skipped {filename}")

def fetch_top_100():
    # Fetch the Hot 100 chart
    chart = billboard.ChartData('artist-100')

    # Initialize a dictionary to count appearances
    artists = []

    # Iterate through the chart entries
    for song in chart:
        artist_name = song.artist
        artists.append(artist_name)

    return artists 

if __name__ == '__main__':
    for artist in fetch_top_100():
        pull_artist(artist)
        separate_stems(artist)