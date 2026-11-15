import os
import sys
import requests

SAVE_DIR = "music"
os.makedirs(SAVE_DIR, exist_ok=True)

# Wikimedia requires a descriptive User-Agent header with a project name/URL
headers = {
    "User-Agent": "RaveMusicRepoUpdater/1.0 (https://github.com; automated-study-project)"
}

api_url = "https://wikimedia.org"
params = {
    "action": "query",
    "generator": "search",
    "gsrsearch": "filetype:audio (techno OR rave OR electronic)",
    "gsrnamespace": 6,
    "gsrlimit": 20,
    "prop": "imageinfo",
    "iiprop": "url|size",
    "format": "json",
}

response = requests.get(api_url, params=params, headers=headers, timeout=30)
if response.status_code != 200:
    print(f"Wikimedia API error {response.status_code}: {response.text[:300]}")
    sys.exit(1)

data = response.json()
pages = data.get("query", {}).get("pages", {})
print(f"Wikimedia returned {len(pages)} audio files.")

downloaded_count = 0

for page_id, page_data in pages.items():
    if downloaded_count >= 3:
        break

    title = page_data.get("title", "").replace("File:", "")
    info_list = page_data.get("imageinfo", [])
    if not info_list:
        continue

    file_url = info_list[0].get("url", "")
    file_size = info_list[0].get("size", 0)

    # Filter for files between 500 KB and 25 MB (safe for GitHub's 100 MB limit)
    if not file_url or not (500_000 < file_size < 25_000_000):
        continue

    safe_name = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_", ".")).rstrip()
    filepath = os.path.join(SAVE_DIR, safe_name)

    if os.path.exists(filepath):
        continue

    print(f"Downloading: {safe_name}")
    audio_resp = requests.get(file_url, headers=headers, timeout=60)
    if audio_resp.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(audio_resp.content)
        print(f"Saved: {filepath}")
        downloaded_count += 1

if downloaded_count == 0:
    print("No new tracks downloaded on this run.")
