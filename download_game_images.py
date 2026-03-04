import json
import os
import re
import requests
from slugify import slugify
from tqdm import tqdm
from PIL import Image
from io import BytesIO
import zipfile

JSON_PATH = "funpay_games_full.json"
OUT_DIR = "game-images"
ZIP_NAME = "games.zip"

os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "GameImageDownloader/1.0"
}

ALIASES = {
    "counter-strike 2": "cs2",
    "counter-strike: go": "csgo",
    "dota 2": "dota",
    "league of legends": "lol",
    "call of duty": "cod",
}

def normalize_name(name: str) -> str:
    n = name.lower().strip()
    if n in ALIASES:
        return ALIASES[n]
    n = re.sub(r"[™®©]", "", n)
    n = re.sub(r"[^\w\s-]", "", n)
    return slugify(n)

def safe_get(url, params=None, timeout=15):
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
        if r.status_code == 200:
            return r
    except requests.RequestException:
        return None
    return None

def wiki_summary(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    r = safe_get(url)
    if not r:
        return None

    try:
        data = r.json()
    except Exception:
        return None

    if "thumbnail" in data:
        return data["thumbnail"]["source"]
    return None

def wiki_search(title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": title,
        "format": "json",
    }
    r = safe_get(url, params=params)
    if not r:
        return None

    try:
        data = r.json()
    except Exception:
        return None

    if not data.get("query", {}).get("search"):
        return None

    best = data["query"]["search"][0]["title"]
    return wiki_summary(best)

def download_png(url):
    r = safe_get(url, timeout=20)
    if not r:
        return None
    try:
        img = Image.open(BytesIO(r.content)).convert("RGBA")
        return img
    except Exception:
        return None

with open(JSON_PATH, "r", encoding="utf-8") as f:
    games = json.load(f)

saved = []

for g in tqdm(games):
    name = g["name"]
    fname = normalize_name(name) + ".png"
    path = os.path.join(OUT_DIR, fname)

    if os.path.exists(path):
        try:
            with Image.open(path) as im:
                im.verify()
            saved.append(path)
            continue
        except Exception:
            pass

    img_url = wiki_summary(name)

    if not img_url:
        img_url = wiki_search(name)

    if not img_url:
        continue

    img = download_png(img_url)
    if not img:
        continue

    img.save(path, "PNG")
    saved.append(path)

with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as z:
    for p in saved:
        z.write(p, os.path.basename(p))

print(f"Saved {len(saved)} images")
print(f"ZIP: {ZIP_NAME}")