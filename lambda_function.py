import json
import os
import requests

def read_secrets() -> dict:
    filename = os.path.join('secrets.json')
    try:
        with open(filename, mode='r') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        return {}

secrets = read_secrets()
apikey =  secrets["apikey"]
playlistId = secrets["playlistId"]
api_service_name = "youtube"
api_version = "v3"
URL = "https://youtube.googleapis.com/" + api_service_name + "/" + api_version 

def Get_Playlist_Items(playlistId: str, nextPageToken: str, itemcount: int) -> list:
    maxResults=50
    ids = []
    url = URL + "/" + "playlistItems"
    if nextPageToken == "": #If no page token supplied assuming first call
        params = {
            "part": "contentDetails",
            "maxResults": maxResults,
            "playlistId": playlistId,
            "key": apikey
        }
    else:
        params = {
            "part": "contentDetails",
            "maxResults": maxResults,
            "playlistId": playlistId,
            "pageToken": nextPageToken,
            "key": apikey
        }
    response = requests.get(url= url, params=params).json()
    totalResults = response["pageInfo"]["totalResults"]
    itemcount += len(response["items"])

    for item in response["items"]:
        ids.append(str(item["contentDetails"]["videoId"]))

    if itemcount < totalResults:
        pageToken = response["nextPageToken"]
        ids = ids + Get_Playlist_Items(playlistId,pageToken,itemcount)
    return ids

def Count_Views(ids: list, itemcount: int) -> dict:
    stats = {"views": 0, "likes": 0}
    maxResults=50
    url = URL + "/" + "videos"
    videoids = ids[itemcount:itemcount+50]
    params = {
        "part": "statistics",
        "maxResults": maxResults,
        "id": ",".join(videoids),
        "key": apikey
    }
    response = requests.get(url= url, params=params).json()
    if len(ids) > len(videoids):
        Count_Views(ids[itemcount + 50:], itemcount + len(videoids))
    for item in response["items"]:
        item = item["statistics"]
        stats["views"] += int(item["viewCount"])
        stats["likes"] += int(item["likeCount"])
    return stats

def lambda_handler(event, context):
    ids = Get_Playlist_Items(playlistId,"",0)
    stats = Count_Views(ids,0)
    return {
        'statusCode': 200,
        'body': json.dumps(stats)
    }