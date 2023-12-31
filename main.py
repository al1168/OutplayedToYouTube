# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import logging
import os
from fastapi import FastAPI, HTTPException
import google_auth_oauthlib
import googleapiclient
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.credentials import Credentials

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_SECRETS_FILE = "client_secrets.json"


def upload_video(youtube_service_obj, title="", description="", file_path=""):
    """
    :param youtube_service_obj:
    :param title:
    :param description:
    :param file_path:
    :return: response
    """
    if youtube_service_obj is None:
        raise Exception("no youtube Service obj")
    youtube_insert_body = dict(
        snippet=dict(
            title=title,
            description=description,
            categoryId=20,
        ),
        status=dict(privacyStatus="unlisted"),
    )
    insert_request = youtube_service_obj.videos().insert(
        part="snippet,status",
        body=youtube_insert_body,
        media_body=googleapiclient.http.MediaFileUpload(file_path),
    )
    response = insert_request.execute()
    logging.info("THIS IS RESPONSE %s", response)
    return response


def get_video_src(page_url):
    """

    :param page_url:
    :return:
    """
    try:
        # print(page_url)
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, "html.parser")
        video_main = soup.find(class_="video-main")
        video_tag = soup.find("video")
        print(f"THIS IS PAGE URL {page_url} THIS IS VIDEO TAG {video_tag}")
        return video_tag.get("src", None)
    except Exception as e:
        logging.error("ERROR IN getting video_src from url", page_url)


def download_outplayed_video(video_src_url, index):
    """

    :param video_src_url:
    :param index:
    :return:
    """
    try:
        response = requests.get(video_src_url, stream=True)
        if response.status_code == 200:
            temp_file_name = f"temp_file_{index}.mp4"
            with open(temp_file_name, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            logging.info(
                f"Outplayed video src {video_src_url} downloaded -> {temp_file_name}"
            )
            return temp_file_name
        else:
            logging.warning(f"Could not retrieve video. Status: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"an Error as occurred downloading outplayed video :{e}")
        return False


from pydantic import BaseModel


def get_youtube_client(access_token: str):
    credentials = Credentials(token=access_token)
    return build("youtube", "v3", credentials=credentials)


def get_youtube_service(credentials):
    """
    :param credentials:
    :return:
    """
    youtube_service = build(
        serviceName=API_SERVICE_NAME, version=API_VERSION, credentials=credentials
    )
    return youtube_service


def get_google_authentication():
    """

    :return:
    """
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES
    )
    credentials = flow.run_local_server()
    return credentials


def main(request_payload):
    # pass

    """

    :param request_payload: dict
    :return:
    """
    url = request_payload.get("outplayed_url", None)
    title = request_payload.get("title", None)
    description = request_payload.get("description", None)
    if url is None:
        logging.error("No 'outplayed_url' found in the request payload")
        return
    try:
        # Attempt to retrieve video source and download the video
        client_oauth_credentials = get_google_authentication()
        client_youtube_service = get_youtube_service(client_oauth_credentials)
        video_src = get_video_src(url)
        file_path = download_outplayed_video(video_src, 1)
        if file_path is False:
            logging.error(
                "FAILED to download Video for request_payload %s", request_payload
            )
            return

        logging.info("Video downloaded successfully %s", file_path)
        response = upload_video(
            youtube_service_obj=client_youtube_service,
            title=title,
            description=description,
            file_path=file_path,
        )

        os.remove(file_path)

    except Exception as e:
        # Log the exception details
        logging.error("An error occurred during video processing: %s", e)
        # Optionally, you might want to re-raise the exception or handle it differently


# Press the green button in the gutter to run the script.
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


class UploadPayLoad(BaseModel):
    token: str
    url: str
    title: str
    description: str


@app.post("/upload_videos")
async def upload_video_endpoint(payload: UploadPayLoad):
    print(payload)
    token, url, title, description = payload
    # print(token)
    # Your logic here
    # get_video_src(url[1])
    print(f"THIS IS REQUEST TITLE:{title}")
    print(f"THIS IS REQUEST DESCRIPTION:{description}")
    youtube_client = get_youtube_client(token[1])
    if url is None:
        logging.error("No 'outplayed_url' found in the request payload")
        return
    try:
        # Attempt to retrieve video source and download the video
        video_src = get_video_src(url[1])
        file_path = download_outplayed_video(video_src, 1)
        if file_path is False:
            logging.error(
                "FAILED to download Video for request_payload",
            )
            return
        logging.info("Video downloaded successfully %s", file_path)
        print(youtube_client)
        upload_video(
            youtube_service_obj=youtube_client,
            title=title[1],
            description=description[1],
            file_path=file_path,
        )
        os.remove(file_path)

    except Exception as e:
        # Log the exception details
        # os.remove(file_path)
        logging.error("An error occurred during video processing: %s", e)
        # Optionally, you might want to re-raise the exception or handle it differently
        raise HTTPException(
            status_code=404, detail=f"An error occurred during video processing: {e}"
        )
    return {"message": f"Sucesss!"}


if __name__ == "__main__":
    payload = {}
    questions = {
        "Enter video url": "outplayed_url",
        "Enter a title": "title",
        "Enter a description": "description",
    }
    for question, payload_key in questions.items():
        print(question)
        user_input = input()
        payload[payload_key] = user_input
    main(payload)
# pass

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
