# SpoTube
Simple python script to convert spotify playlists into youtube playlists

To install this script:

```
git clone https://github.com/Lerzy/SpoTube.git
cd SpoTube
pip install -r requirements.txt
```

after you have installed the script, you need a spotify api credientials and youtube oauth:

Spotify credientials go into `spotify_creds.py` and youtube oauth json file goes into `client_secret.json` 

after that the script can be run with:
```
python spotube.py -pl <Spotify playlist url> -pid <OPTIONAL if left empty a new playlist will be created> 
```
