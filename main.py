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
parser.add_argument("-un", "--username", help="Your spotify username")
parser.add_argument("-pl", "--playlist_url", help="Spotify playlist url to convert")
parser.add_argument("-pid", "--playlist_id", help="Youtube playlist id where to add songs")
args = parser.parse_args()




username = args.username
url = args.playlist_url
playlist_id = args.playlist_id



def auth_youtube():
    scopes = ["https://www.googleapis.com/auth/youtube"]

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
    credentials = flow.run_console()

    youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

    return youtube



def create_track_list(username, playlist_id):
    """creates a list of youtube search queries (artist - song name) to be used in playlist creation"""
    client_credentials_manager = SpotifyClientCredentials(client_id=spotify_creds.SPOTIPY_CLIENT_ID,
                                                      client_secret=spotify_creds.SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    for i in tracks:
        track_list.append(i['track']['artists'][0]['name'] + " - " + i['track']['name'])
        
    return track_list

def create_id_list(track_list):
    prog = tqdm(track_list)

    ydl_opts = {
        'quiet': True
    }

    for search_query in prog:
        with YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info('ytsearch:%s' % search_query, download=False)
            if 'entries' in data and data['entries'] != []:
                info = data['entries'][0]
                id_list.append(info['id'])
        prog.set_description("Creating track id list (this might take a while) %s" % search_query)
    return id_list

def add_to_playlist(youtube, id_list, playlist_id):

    """batch = youtube.new_batch_http_request()"""
    for videoId in id_list:
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

        print(f"\n{response}")


if __name__ == "__main__":
    authed_youtube = auth_youtube()
    track_list = create_track_list(username, url)
    id_list = create_id_list(track_list)
    add_to_playlist = add_to_playlist(authed_youtube, id_list, playlist_id)
    print(f"Done! Check your youtube playlist: \n https://youtube.com/playlist?list={playlist_id}")