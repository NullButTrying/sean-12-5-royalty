import os
import sys
import requests

API_KEY = os.environ.get("MUSIC_API_KEY", "").strip()
if not API_KEY:
    print("Error: MUSIC_API_KEY environment variable is empty.")
    sys.exit(1)

SAVE_DIR = "music"
os.makedirs(SAVE_DIR, exist_ok=True)

url = "https://freesound.org"
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; RaveMusicBot/1.0)",
    "Authorization": f"Token {API_KEY}",
}
params = {
    "query": "rave",
    "filter": "duration:[30 TO 300]",
    "fields": "id,name,previews,license",
    "page_size": 3,
}

response = requests.get(url, headers=headers, params=params)

if response.status_code != 200:
    print(f"Freesound API failed with status {response.status_code}:")
    print(response.text[:500])
    sys.exit(1)

data = response.json()

for track in data.get("results", []):
    track_id = track["id"]
    safe_name = "".join(c for c in track["name"] if c.isalnum() or c in (" ", "-", "_")).rstrip()
    filename = f"{SAVE_DIR}/{track_id}_{safe_name}.mp3"
    
    if os.path.exists(filename):
        continue
        
    audio_url = track["previews"]["preview-hq-mp3"]
    audio_data = requests.get(audio_url, headers=headers).content
    
    with open(filename, "wb") as f:
        f.write(audio_data)
    print(f"Downloaded: {filename}")
