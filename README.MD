Lambda function to return total of views and likes of provided playlist ID.

## Requirements
1. AWS Account and Lambda..
2. Youtube api key.
    You can read how to get one from here: https://developers.google.com/youtube/v3/quickstart/python#step_1_set_up_your_project_and_credentials

## secrets.json

{
    "apikey": "YOUR_API_KEY",
    "playlistId": "YOUR_PLAYLIST_ID"
}

## TO Use

1. Clone the repository
2. Create secrets.json
3. ZIP repository to object.zip
4. Create Lambda with Python 3.7 runtime (This is important as 3.9 doesn't have requests)
5. Upload to Lambda
6. ???
7. Profit
