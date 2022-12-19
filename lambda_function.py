import json
import os
import sys
sys.path.append('./package')
import googleapiclient.discovery


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
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
api_service_name = "youtube"
api_version = "v3"
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = apikey)

ids = []
stats = {"views": 0, "likes": 0}

def Get_Playlist_Items(playlistId: str, nextPageToken: str, itemcount: int) -> None:
    maxResults=50

    if nextPageToken == "": #If no page token supplied assuming first call
        request = youtube.playlistItems().list(
            part="contentDetails",
            maxResults=maxResults,
            playlistId=playlistId
        )
    else:
        request = youtube.playlistItems().list(
            part="contentDetails",
            maxResults=maxResults,
            pageToken=nextPageToken,
            playlistId=playlistId
        )
    response = request.execute()
    totalResults = response["pageInfo"]["totalResults"]
    itemcount += len(response["items"])

    for item in response["items"]:
        ids.append(str(item["contentDetails"]["videoId"]))

    if itemcount < totalResults:
        pageToken = response["nextPageToken"]
        Get_Playlist_Items(playlistId,pageToken,itemcount)
    return

def Count_Views(ids: list, itemcount: int) -> None:

    videoids = ids[itemcount:itemcount+50]

    request = youtube.videos().list(
        part="statistics",
        id=",".join(videoids)
    )
    response = request.execute()

    if len(ids) > len(videoids):
        Count_Views(ids[itemcount + 50:], itemcount + len(videoids))

    for item in response["items"]:
        item = item["statistics"]
        stats["views"] += int(item["viewCount"])
        stats["likes"] += int(item["likeCount"])
    return

def lambda_handler(event, context):
    Get_Playlist_Items(playlistId,"",0)
    Count_Views(ids,0)
    return {
        'statusCode': 200,
        'body': json.dumps(stats)
    }