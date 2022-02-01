import spotipy
import spotify_creds
from spotipy import SpotifyClientCredentials
from yt_dlp import YoutubeDL
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from tqdm import tqdm
import argparse

track_list = []

id_list = []

parser = argparse.ArgumentParser(description='Convert spotify playlists into youtube playlists')
parser.add_argument("-pl", "--playlist_url", help="Spotify playlist url to convert")
parser.add_argument("-pid", "--playlist_id", nargs="?", default=None ,help="(OPTIONAL) Youtube playlist id where to add songs")
args = parser.parse_args()


url = args.playlist_url
playlist_id = args.playlist_id


def auth_youtube():
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
    credentials = flow.run_console()

    youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

    return youtube



def create_track_list(playlist):
    """creates a list of youtube search queries (artist - song name) to be used in playlist creation"""
    client_credentials_manager = SpotifyClientCredentials(client_id=spotify_creds.SPOTIPY_CLIENT_ID,
                                                      client_secret=spotify_creds.SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    playlist_name = sp.user_playlist(user=None, playlist_id = playlist, fields="name")['name']
    results = sp.user_playlist_tracks(user=None, playlist_id = playlist)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    for i in tracks:
        track_list.append(i['track']['artists'][0]['name'] + " - " + i['track']['name'])
        
    return playlist_name, track_list

def create_id_list(track_list):
    prog = tqdm(track_list)

    ydl_opts = {
        'quiet': True
    }

    for search_query in prog:
        with YoutubeDL(ydl_opts) as ydl:
            prog.set_description("Searching youtube for songs: %s" % search_query)
            data = ydl.extract_info('ytsearch:%s' % search_query, download=False)
            if 'entries' in data and data['entries'] != []:
                info = data['entries'][0]
                id_list.append(info['id'])
    return id_list


def add_to_playlist(youtube, id_list, playlist_id):
    upload_prog = tqdm(id_list)
    """batch = youtube.new_batch_http_request()"""
    for videoId in upload_prog:
        upload_prog.set_description("Uploading songs to playlist")
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                "playlistId": playlist_id, 
                "position": 0,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": videoId 
                }
                }
            }
        )
        response = request.execute()

        
        
def create_playlist(youtube, playlist_name):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": playlist_name,
            "description": "Converted from spotify",
          },
          "status": {
            "privacyStatus": "private"
          }
        }
    )
    response = request.execute()
    return response['id']


if __name__ == "__main__":
    authed_youtube = auth_youtube()
    playlist_name, track_list = create_track_list(url)
    if playlist_id == None:
        playlist_id = create_playlist(authed_youtube, playlist_name)
    id_list = create_id_list(track_list)
    add_to_playlist = add_to_playlist(authed_youtube, id_list, playlist_id)
    print(f"Done! Check your youtube playlist: \n https://youtube.com/playlist?list={playlist_id}")