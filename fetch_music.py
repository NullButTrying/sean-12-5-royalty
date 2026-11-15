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
headers = {
    "User-Agent": "RaveMusicRepoBot/1.0",
    "Accept": "application/json",
}
params = {
    "client_id": CLIENT_ID,
    "format": "json",
    "limit": 15,
    "fuzzytags": "rave",
    "audioformat": "mp32",
    "order": "popularity_week",
    "include": "licenses",
}

response = requests.get(api_url, params=params, headers=headers, timeout=30)

try:
    data = response.json()
except Exception:
    print(f"Jamendo returned non-JSON (Status {response.status_code}, Length {len(response.text)}):")
    print(repr(response.text[:500]))
    sys.exit(1)

# Check if Jamendo returned an API-level error message inside JSON
header_info = data.get("headers", {})
if header_info.get("status") == "failed":
    print(f"Jamendo API error: {header_info.get('error_message')}")
    sys.exit(1)

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
    audio_resp = requests.get(download_url, headers=headers, timeout=60)
    if audio_resp.status_code == 200 and len(audio_resp.content) > 100_000:
        with open(filepath, "wb") as f:
            f.write(audio_resp.content)
        print(f"Saved: {filepath}")
        downloaded_count += 1

if downloaded_count == 0:
    print("No new downloadable tracks found on this run.")
