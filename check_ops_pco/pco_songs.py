"""Gets all songs from planning center"""

import json
import os

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

all_songs = []

basic = HTTPBasicAuth(
    os.getenv("CLIENT_ID", ""),
    os.getenv("SECRET", ""),
)
page_count_req: dict = requests.get(
    "https://api.planningcenteronline.com/services/v2/songs?per_page=1",
    auth=basic,
).json()
total = page_count_req.get("meta", {"total_count": 0}).get("total_count", 0)

for offset in range(0, total, 100):
    result: dict = requests.get(
        f"https://api.planningcenteronline.com/services/v2/songs?per_page=100&offset={offset}",
        auth=basic,
    ).json()
    songs = result.get("data", [])
    for song in songs:
        all_songs.append(song.get("attributes", {"title", None}).get("title", None))

with open("pco_songs.json", "w") as fp:
    json.dump(all_songs, fp, indent=4, sort_keys=True)
