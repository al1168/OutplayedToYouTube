# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

"""
Client ID : 1037465814913-7oklnlu5f8u8b6308b9vk131vv134o86.apps.googleusercontent.com
Client secret: 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
"""
import sys

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google_auth_oauthlib.flow
import requests
from bs4 import BeautifulSoup


def upload_video(client_id, client_secret):
    pass


#   return {
# "web": {
#   "client_id": client_id,
#   "client_secret": client_secret,
#   "redirect_uris": [],
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://accounts.google.com/o/oauth2/token"
# }
# }

# SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_SECRETS_FILE = "client_secrets.json"


def get_video_src(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")
    video_main = soup.find(class_="video-main")
    video_tag = soup.find("video")

    return video_tag.get("src", None)


def download_outplayed_video(video_src_url, index):
    response = requests.get(video_src_url, stream=True)
    if response.status_code == 200:
        temp_file_name = f'temp_file_{index}'
        with open(temp_file_name, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Outplayed video src {video_src_url} downloaded -> {temp_file_name}")
    else:
        print(f"could not retrieve video Status {response.status_code}")


def get_google_authentication():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES
    )
    credentials = flow.run_local_server(port=0)
    youtube_service = build(
        serviceName=API_SERVICE_NAME, version=API_VERSION, credentials=credentials
    )

def main(url):
    video_src = get_video_src(url)
    download_outplayed_video(video_src,1)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    url = sys.argv[1]
    main(url)
    # get_google_authentication()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
