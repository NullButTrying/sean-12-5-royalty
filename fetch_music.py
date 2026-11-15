import os
import sys
import requests

SAVE_DIR = "music"
os.makedirs(SAVE_DIR, exist_ok=True)

# Use Internet Archive's official Scrape API designed for automated scripts
search_url = "https://archive.org"
params = {
    "q": 'mediatype:audio AND (subject:rave OR subject:techno) AND (licenseurl:*creativecommons* OR licenseurl:*publicdomain*)',
    "fields": "identifier,title",
    "count": 15,
}

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; RaveMusicRepoUpdater/1.0; +https://github.com)",
    "Accept": "application/json",
}

response = requests.get(search_url, params=params, headers=headers, timeout=30)

if response.status_code != 200 or not response.text.strip():
    print(f"Search failed (Status {response.status_code}): {response.text[:300]}")
    sys.exit(1)

items = response.json().get("items", [])
print(f"Found {len(items)} candidate collections.")
downloaded_count = 0

for item in items:
    if downloaded_count >= 3:
        break

    identifier = item["identifier"]
    meta_url = f"https://archive.org{identifier}"
    meta_resp = requests.get(meta_url, headers=headers, timeout=30)
    if meta_resp.status_code != 200:
        continue

    files = meta_resp.json().get("files", [])
    for file_info in files:
        name = file_info.get("name", "")
        try:
            size = int(file_info.get("size", 0))
        except ValueError:
            size = 0

        # Pick MP3 files between 1 MB and 25 MB
        if name.lower().endswith(".mp3") and 1_000_000 < size < 25_000_000:
            safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_", ".")).rstrip()
            filepath = f"{SAVE_DIR}/{identifier}_{safe_name}"

            if os.path.exists(filepath):
                continue

            download_url = f"https://archive.org{identifier}/{name}"
            print(f"Downloading: {download_url}")
            audio_resp = requests.get(download_url, headers=headers, timeout=60)

            if audio_resp.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(audio_resp.content)
                print(f"Saved: {filepath}")
                downloaded_count += 1
                break

if downloaded_count == 0:
    print("No new matching MP3 files were downloaded on this run.")
