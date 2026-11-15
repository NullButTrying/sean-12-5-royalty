import os
import requests

SAVE_DIR = "music"
os.makedirs(SAVE_DIR, exist_ok=True)

# Search Internet Archive for Creative Commons / Public Domain rave audio
search_url = "https://archive.org"
params = {
    "q": 'subject:(rave OR techno) AND mediatype:(audio) AND licenseurl:(*creativecommons* OR *publicdomain*)',
    "fl[]": ["identifier", "title"],
    "sort[]": "downloads desc",
    "rows": 10,
    "page": 1,
    "output": "json",
}

headers = {"User-Agent": "GitHubActionsRaveMusicBot/1.0"}
response = requests.get(search_url, params=params, headers=headers)
response.raise_for_status()

items = response.json().get("response", {}).get("docs", [])
downloaded_count = 0

for item in items:
    if downloaded_count >= 3:
        break

    identifier = item["identifier"]
    meta_url = f"https://archive.org{identifier}"
    meta_resp = requests.get(meta_url, headers=headers)
    if meta_resp.status_code != 200:
        continue

    files = meta_resp.json().get("files", [])
    for file_info in files:
        name = file_info.get("name", "")
        size = int(file_info.get("size", 0))

        # Look for MP3 files between 1 MB and 25 MB (safe for GitHub's 100 MB limit)
        if name.lower().endswith(".mp3") and 1_000_000 < size < 25_000_000:
            safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_", ".")).rstrip()
            filepath = f"{SAVE_DIR}/{identifier}_{safe_name}"

            if os.path.exists(filepath):
                continue

            download_url = f"https://archive.org{identifier}/{name}"
            print(f"Downloading: {download_url}")
            audio_resp = requests.get(download_url, headers=headers)

            if audio_resp.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(audio_resp.content)
                print(f"Saved: {filepath}")
                downloaded_count += 1
                break
