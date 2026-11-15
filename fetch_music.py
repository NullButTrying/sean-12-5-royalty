import os
import requests

API_KEY = os.environ.get("MUSIC_API_KEY")
SAVE_DIR = "music"
os.makedirs(SAVE_DIR, exist_ok=True)

# Search Freesound for rave tracks
url = "https://freesound.org"
params = {
    "query": "rave",
    "filter": "duration:[30 TO 300]",
    "fields": "id,name,previews,license",
    "page_size": 3,
    "token": API_KEY,
}

response = requests.get(url, params=params)
data = response.json()

for track in data.get("results", []):
    track_id = track["id"]
    # Clean filename
    safe_name = "".join(c for c in track["name"] if c.isalnum() or c in (" ", "-", "_")).rstrip()
    filename = f"{SAVE_DIR}/{track_id}_{safe_name}.mp3"
    
    # Skip if already downloaded
    if os.path.exists(filename):
        continue
        
    audio_url = track["previews"]["preview-hq-mp3"]
    audio_data = requests.get(audio_url).content
    
    with open(filename, "wb") as f:
        f.write(audio_data)
    print(f"Downloaded: {filename}")
