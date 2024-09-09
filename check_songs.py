"""Small script to check if the song exists in planning center under the same name but is missing the song number"""

import json
import os

same_songs: list[str] = []
ops_songs: list[dict[str, str]] | None = None
pco_songs: list[str] | None = None

with open("ops_songs.json") as f:
    ops_songs = json.load(f)

with open("pco_songs.json") as f:
    pco_songs = json.load(f)

if pco_songs is None or ops_songs is None:
    print("Generate the json files first")
    exit()

lowercase_pco_songs = [song.lower() for song in pco_songs]

with open("check_songs.txt", "w") as fp:
    for song in ops_songs:
        title = song.get("title", "")
        if title.lower() in lowercase_pco_songs:
            fp.write(f"{song.get('book', '')}: {title} {os.linesep}")
