import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import json
import re
import pandas as pd

dir_path = os.path.dirname(os.path.realpath(__file__))
load_dotenv()


def highlight_non_section_text(full_text, sections):
    # Escape special characters in sections for regex
    escaped_sections = [re.escape(section) for section in sections]

    # Combine all sections into one regex pattern
    pattern = "|".join(escaped_sections)

    # Find all matches (sections to keep)
    matches = list(re.finditer(pattern, full_text))

    # Build the highlighted HTML
    result = ""
    last_index = 0
    total_red = 0

    for match in matches:
        start, end = match.span()
        # Add red-highlighted text before the match
        if start > last_index:
            red_text = full_text[last_index:start]
            total_red += len(red_text)
            result += f"<span style='color:red'>{red_text}</span>"
        # Add the matched section in normal color
        result += f"<span style='color:black'>{match.group()}</span>"
        last_index = end

    # Add any remaining text after the last match
    if last_index < len(full_text):
        red_text = full_text[last_index:]
        total_red += len(red_text)
        result += f"<span style='color:red'>{red_text}</span>"

    return result, total_red


def get_song_info(song_id, song_name) -> list[tuple[int, int, int, int]]:
    print(song_name)
    basic = HTTPBasicAuth(
        os.getenv("CLIENT_ID", ""),
        os.getenv("SECRET", ""),
    )
    result: dict = requests.get(
        f"https://api.planningcenteronline.com/services/v2/songs/{song_id}/arrangements/",
        auth=basic,
    ).json()

    arrangement_results = []

    for arrangement in result.get("data", {}):
        arrangement_id: int = arrangement.get("id", "")
        lyrics = arrangement.get("attributes", {}).get("lyrics", "")
        if lyrics is None:
            continue
        sections_data: dict = requests.get(
            f"https://api.planningcenteronline.com/services/v2/songs/{song_id}/arrangements/{arrangement_id}/sections",
            auth=basic,
        ).json()
        section_texts = []
        sections = (
            sections_data.get("data", {}).get("attributes", {}).get("sections", [])
        )

        with open(
            f"{dir_path}/sections/{song_name.replace('/', '-')}_{arrangement_id}.json",
            "w",
        ) as d:
            json.dump(sections, d, indent=4, sort_keys=True)

        longest_section_length = 0
        for section in sections:
            section_texts.append(section.get("label", ""))
            current: str = (
                section.get("lyrics", "")
                .replace("\n\r", "\n")
                .replace("\r\n", "\n")
                .replace("\r", "\n")
            )
            section_texts.append(current)
            section_length = current.count("\n")
            if section_length > longest_section_length:
                longest_section_length = section_length

        html_output, total_section_red = highlight_non_section_text(
            lyrics.replace("\n\n", "\n"), section_texts
        )

        # Save to file or display in browser
        with open(
            f"{dir_path}/results/{song_name.replace('/', '-')}_{arrangement_id}.html",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(f"<html><body>{html_output.replace('\n', '<br />')}</body></html>")
        arrangement_results.append(
            (total_section_red, arrangement_id, len(sections), longest_section_length)
        )
    return arrangement_results


total = []
if os.path.exists("result.json"):
    with open("result.json") as d:
        total = json.load(d)


def all():
    with open(f"{dir_path}/pco_songs_dict.json") as f:
        ops_songs = json.load(f)

        for key, value in ops_songs.items():
            if not any(item["song_id"] == key for item in total):
                results = get_song_info(key, value)
                for result in results:
                    (
                        total_red,
                        arrangement_id,
                        total_sections,
                        longest_section_length,
                    ) = result
                    total.append(
                        {
                            "song_id": key,
                            "song_name": value,
                            "arragement_id": arrangement_id,
                            "total_red": total_red,
                            "total_sections": total_sections,
                            "longest_section_length": longest_section_length,
                            "edit_url": f"https://services.planningcenteronline.com/songs/{key}/arrangements/{arrangement_id}/chord_chart/edit",
                        }
                    )
                    with open("result.json", "w") as d:
                        json.dump(total, d, indent=4, sort_keys=True)
        df = pd.DataFrame(total)
        print(df)
        df.to_csv("result.csv", index=False)


def song(song_id):
    with open(f"{dir_path}/pco_songs_dict.json") as f:
        ops_songs = json.load(f)

        song_name = ops_songs.get(song_id)
        results = get_song_info(song_id, song_name)
        for result in results:
            total_red, arrangement_id, total_sections, longest_section_length = result
            total.append(
                {
                    "song_id": song_id,
                    "song_name": song_name,
                    "arrangement_id": arrangement_id,
                    "total_red": total_red,
                    "total_sections": total_sections,
                    "longest_section_length": longest_section_length,
                    "edit_url": f"https://services.planningcenteronline.com/songs/{song_id}/arrangements/{arrangement_id}/chord_chart/edit",
                }
            )
            with open("result.json", "w") as d:
                json.dump(total, d, indent=4, sort_keys=True)
        df = pd.DataFrame(total)
        print(df)
        df.to_csv("result.csv", index=False)


if __name__ == "__main__":
    all()
