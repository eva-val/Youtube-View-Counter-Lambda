from typing import Dict, List
import os, time
import json, requests

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


def get_playlist_items(
    playlistId: str, apikey: str, nextPageToken: str = "", itemcount: int = 0
) -> List:
    max_results = 50
    ids = []
    url = URL + "/" + "playlistItems"
    if nextPageToken == "":  # If no page token supplied assuming first call
        params = {
            "part": "contentDetails",
            "maxResults": max_results,
            "playlistId": playlistId,
            "key": apikey,
        }
    else:
        params = {
            "part": "contentDetails",
            "maxResults": max_results,
            "playlistId": playlistId,
            "pageToken": nextPageToken,
            "key": apikey,
        }
    response = requests.get(url=url, params=params, timeout=10).json()
    totalResults = response["pageInfo"]["totalResults"]
    itemcount += len(response["items"])

    for item in response["items"]:
        ids.append(str(item["contentDetails"]["videoId"]))

    if itemcount < totalResults:
        pageToken = response["nextPageToken"]
        ids += get_playlist_items(
            playlistId=playlistId,
            apikey=apikey,
            nextPageToken=pageToken,
            itemcount=itemcount,
        )
    return ids


def count_views(ids: list, apikey: str, itemcount: int = 0) -> Dict:
    stats = {"views": 0, "likes": 0}
    max_results = 50
    url = f"{URL}/videos"
    videoids = ids[itemcount : itemcount + 50]
    params = {
        "part": "statistics",
        "maxResults": max_results,
        "id": ",".join(videoids),
        "key": apikey,
    }
    response = requests.get(url=url, params=params, timeout=10).json()
    if len(ids) > len(videoids):
        count_views(
            ids=ids[itemcount + 50 :],
            apikey=apikey,
            itemcount=itemcount + len(videoids),
        )
    for item in response["items"]:
        item = item["statistics"]
        stats["views"] += int(item["viewCount"])
        stats["likes"] += int(item["likeCount"])
    return stats


# def lambda_handler(event, context):
#     secrets = read_secrets()
#     apikey = secrets["apikey"]
#     playlistId = secrets["playlistId"]
#     ids = get_playlist_items(playlistId=playlistId, apikey=apikey)
#     stats = count_views(ids=ids, apikey=apikey)
#     return {"statusCode": 200, "body": json.dumps(stats)}


if __name__ == "__main__":
    start = time.time()
    secrets = read_secrets()
    apikey = secrets["apikey"]
    playlistId = secrets["playlistId"]
    ids = get_playlist_items(playlistId=playlistId, apikey=apikey)
    stats = count_views(ids=ids, apikey=apikey)
    stop = time.time()
    print(stats)
    print(f"Took: {(stop-start)} seconds")