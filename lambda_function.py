from typing import List, Tuple
import os
from concurrent.futures import ThreadPoolExecutor
import json
import urllib.request
import urllib.parse
# from dotenv import load_dotenv

# load_dotenv()

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
URL = f"https://youtube.googleapis.com/{API_SERVICE_NAME}/{API_VERSION}"
API_KEY = os.environ["API_KEY"]
PLAYLIST_ID = os.environ["PLAYLIST_ID"]


def fetch_url(url: str, params: dict) -> dict:
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    with urllib.request.urlopen(full_url) as response:
        return json.loads(response.read().decode())


def get_playlist_items() -> List[str]:
    max_results = 50
    url = f"{URL}/playlistItems"
    params = {
        "part": "contentDetails",
        "maxResults": max_results,
        "playlistId": PLAYLIST_ID,
        "key": API_KEY,
    }
    ids = []
    total_results = 0
    item_count = 0
    page_token = None

    while True:
        if page_token:
            params["pageToken"] = page_token
        response = fetch_url(url=url, params=params)
        if item_count == 0:  # Assuming first iteration
            total_results = response["pageInfo"]["totalResults"]
            ids = [None] * total_results  # Preallocate list

        new_ids = [str(item["contentDetails"]["videoId"]) for item in response["items"]]
        ids[item_count : item_count + len(new_ids)] = new_ids
        item_count += len(new_ids)

        if item_count >= total_results:
            break

        page_token = response.get("nextPageToken", None)
        if not page_token:
            break

    return ids


def count_views(video_ids: List[str]) -> Tuple:
    max_results = 50
    url = f"{URL}/videos"
    params = {
        "part": "statistics",
        "maxResults": max_results,
        "id": ",".join(video_ids),
        "key": API_KEY,
    }
    response = fetch_url(url=url, params=params)
    views, likes = 0, 0
    for item in response["items"]:
        item = item["statistics"]
        views += int(item["viewCount"])
        likes += int(item["likeCount"])
    return views, likes


def fetch_and_count():
    ids = get_playlist_items()
    stats = {"views": 0, "likes": 0}

    # Splitting into sublists of 50
    sublist_size = 50
    ids_sublists = [ids[i : i + sublist_size] for i in range(0, len(ids), sublist_size)]

    def process_sublist(fifty_ids):
        nonlocal stats
        views, likes = count_views(video_ids=fifty_ids)
        stats["views"] += views
        stats["likes"] += likes

    # Using ThreadPoolExecutor to run the counting in parallel
    with ThreadPoolExecutor() as executor:
        executor.map(process_sublist, ids_sublists)

    return stats


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps(fetch_and_count()),
    }


# if __name__ == "__main__":
#     import time
#     start = time.time()
#     stats = fetch_and_count()
#     stop = time.time()
#     print(stats)
#     print(f"Took: {(stop-start)} seconds")
