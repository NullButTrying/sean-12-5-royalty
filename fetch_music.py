import os
import sys
import requests

CLIENT_ID = os.environ.get("MUSIC_API_KEY", "").strip()
if not CLIENT_ID:
    print("Error: MUSIC_API_KEY (Jamendo Client ID) is missing.")
    sys.exit(1)

SAVE_DIR = "music"
os.makedirs(SAVE_DIR, exist_ok=True)

api_url = "https://jamendo.com"
params = {
    "client_id": CLIENT_ID,
    "format": "json",
    "limit": 15,
    "tags": "rave+techno",
    "audioformat": "mp32",
    "order": "popularity_week",
    "include": "licenses",
}

response = requests.get(api_url, params=params, timeout=30)
if response.status_code != 200:
    print(f"Jamendo API failed (Status {response.status_code}): {response.text[:300]}")
    sys.exit(1)

data = response.json()
results = data.get("results", [])
print(f"Jamendo returned {len(results)} tracks.")

downloaded_count = 0

for track in results:
    if downloaded_count >= 3:
        break

    if not track.get("audiodownload_allowed", True):
        continue

    track_id = track["id"]
    artist = track.get("artist_name", "Unknown")
    title = track.get("name", "Track")
    download_url = track.get("audiodownload") or track.get("audio")

    if not download_url:
        continue

    raw_name = f"{track_id}_{artist} - {title}.mp3"
    safe_name = "".join(c for c in raw_name if c.isalnum() or c in (" ", "-", "_", ".")).rstrip()
    filepath = os.path.join(SAVE_DIR, safe_name)

    if os.path.exists(filepath):
        continue

    print(f"Downloading: {safe_name}")
    audio_resp = requests.get(download_url, timeout=60)
    if audio_resp.status_code == 200 and len(audio_resp.content) > 100_000:
        with open(filepath, "wb") as f:
            f.write(audio_resp.content)
        print(f"Saved: {filepath}")
        downloaded_count += 1

if downloaded_count == 0:
    print("No new downloadable tracks found on this run.")
