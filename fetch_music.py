import os
import sys
import requests

SAVE_DIR = "music"
os.makedirs(SAVE_DIR, exist_ok=True)

# Internet Archive requires a descriptive User-Agent with contact info to avoid blocks
headers = {
    "User-Agent": "RaveMusicGitHubRepo/1.0 (https://github.com; contact@example.com)",
    "Accept": "application/json",
}

search_url = "https://archive.org"
params = {
    "q": "mediatype:audio AND (rave OR techno) AND licenseurl:creativecommons",
    "fl[]": ["identifier", "title"],
    "rows": 15,
    "page": 1,
    "output": "json",
}

response = requests.get(search_url, params=params, headers=headers, timeout=30)

try:
    data = response.json()
except Exception:
    print(f"Archive.org returned non-JSON (Status {response.status_code}):")
    print(repr(response.text[:500]))
    sys.exit(1)

items = data.get("response", {}).get("docs", [])
print(f"Found {len(items)} candidate items.")
downloaded_count = 0

for item in items:
    if downloaded_count >= 3:
        break

    identifier = item["identifier"]
    meta_url = f"https://archive.org{identifier}"
    meta_resp = requests.get(meta_url, headers=headers, timeout=30)

    try:
        meta_data = meta_resp.json()
    except Exception:
        continue

    for file_info in meta_data.get("files", []):
        name = file_info.get("name", "")
        try:
            size = int(file_info.get("size", 0))
        except ValueError:
            size = 0

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
