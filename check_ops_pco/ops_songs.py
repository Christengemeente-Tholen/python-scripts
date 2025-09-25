"""Gets all songs from songs.search.sqlite file"""

import json
import re
import sqlite3

con = sqlite3.connect("songs.search.sqlite")

cur = con.cursor()

song_list = []

for row in cur.execute("SELECT title FROM song_index"):
    current: str = row[0]

    # Find the book name at the end of the string
    book_search = re.search(r"([^\s\d]+)[\d]+$", current)
    if book_search is None:
        continue
    book_name = book_search.group(1)

    # Find the songnumber
    song_num_search = re.search(r"nn(\d+)nn", current)
    if song_num_search is None:
        continue
    song_number = song_num_search.group(1)

    # Remove songnumber and multiple book entries from song title
    current = current.replace(song_num_search[0], "")
    for i in range(1, 4):
        current = current.replace(book_name[:i] + song_number, "")

    song_list.append(
        {"book": book_name, "song_number": song_number, "title": current.strip()}
    )

con.close()

with open("ops_songs.json", "w") as fp:
    json.dump(song_list, fp, indent=4, sort_keys=True)
