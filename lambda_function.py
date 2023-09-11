from typing import List, Tuple
import os
import json, requests
from concurrent.futures import ThreadPoolExecutor

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
URL = f"https://youtube.googleapis.com/{API_SERVICE_NAME}/{API_VERSION}"


def read_secrets() -> json:
    filename = os.path.join("secrets.json")
    try:
        with open(filename, mode="rb") as file:
            return json.loads(file.read())
    except FileNotFoundError:
        print("secrets.json not found. Is it loaded?")


def get_playlist_items(playlist_items: str, apikey: str) -> List[str]:
    max_results = 50
    url = f"{URL}/playlistItems"
    params = {
        "part": "contentDetails",
        "maxResults": max_results,
        "playlistId": playlist_items,
        "key": apikey,
    }
    ids = []
    total_results = 0
    item_count = 0
    page_token = None

    while True:
        if page_token:
            params["pageToken"] = page_token

        response = requests.get(url=url, params=params, timeout=10).json()

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


def count_views(video_ids: List[str], apikey: str) -> Tuple:
    max_results = 50
    url = f"{URL}/videos"
    params = {
        "part": "statistics",
        "maxResults": max_results,
        "id": ",".join(video_ids),
        "key": apikey,
    }
    response = requests.get(url=url, params=params, timeout=10).json()
    views, likes = 0, 0
    for item in response["items"]:
        item = item["statistics"]
        views += int(item["viewCount"])
        likes += int(item["likeCount"])
        # stats["views"] += int(item["viewCount"])
        # stats["likes"] += int(item["likeCount"])
    # return stats
    return views, likes


def fetch_and_count(playlist_items, apikey):
    ids = get_playlist_items(playlist_items=playlist_items, apikey=apikey)
    stats = {"views": 0, "likes": 0}

    # Splitting into sublists of 50
    sublist_size = 50
    ids_sublists = [ids[i : i + sublist_size] for i in range(0, len(ids), sublist_size)]

    def process_sublist(fifty_ids):
        nonlocal stats
        views, likes = count_views(video_ids=fifty_ids, apikey=apikey)
        stats["views"] += views
        stats["likes"] += likes

    # Using ThreadPoolExecutor to run the counting in parallel
    with ThreadPoolExecutor() as executor:
        executor.map(process_sublist, ids_sublists)

    return stats


def lambda_handler(event, context):
    secrets = read_secrets()
    key = secrets["apikey"]
    playlist_id = secrets["playlistId"]
    return {
        "statusCode": 200,
        "body": json.dumps(fetch_and_count(playlist_items=playlist_id, apikey=key)),
    }


# if __name__ == "__main__":
#     import time
#     start = time.time()
#     secrets = read_secrets()
#     key = secrets["apikey"]
#     playlist_id = secrets["playlistId"]
#     start = time.time()
#     stats = fetch_and_count(playlist_items=playlist_id, apikey=key)
#     stop = time.time()
#     print(stats)
#     print(f"Took: {(stop-start)} seconds")
