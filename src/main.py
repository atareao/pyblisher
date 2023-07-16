#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2022 Lorenzo Carbonell <a.k.a. atareao>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import sys
import logging
import requests
import yt_dlp
from PIL import Image
from dotenv import load_dotenv
from video import Video
from table import Table
from ytapi import YouTube
from threading import Thread
from plumbum import local
from requests_oauthlib import OAuth1
from aupload import VideoTweet
from twitter import Twitter
from mastodonapi import MastodonClient
from fdapi import PeerTube
from zinc import ZincClient
from retry import retry
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from secrets import compare_digest

Table.DATABASE = "/app/database.db"

FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
logging.basicConfig(stream=sys.stdout,
                    format=FORMAT,
                    level=logging.getLevelName(LOG_LEVEL))
logger = logging.getLogger(__name__)

load_dotenv()
Video.inicializate()
app = FastAPI()
security = HTTPBasic()

templates = Jinja2Templates(directory="templates")

PYB_USER = os.getenv("PYB_USER")
PYB_PASSWORD = os.getenv("PYB_PASSWORD")
TW_CONFIG = os.getenv("TW_CONFIG")

zbs = os.getenv("ZINC_BASE_URL", None)
zi = os.getenv("ZINC_INDICE", None)
zt = os.getenv("ZINC_TOKEN", None)
ZC = ZincClient(zbs, zi, zt) if zbs and zi and zt else None


def populate_in_zs(data):
    if ZC:
        ZC.populate(data)


def authorize(credentials: HTTPBasicCredentials = Depends(security)):
    is_user_ok = compare_digest(credentials.username, PYB_USER)
    is_pass_ok = compare_digest(credentials.password, PYB_PASSWORD)

    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password.',
            headers={'WWW-Authenticate': 'Basic'},
            )


@app.get("/status/", dependencies=[Depends(authorize)])
async def get_status():
    return {"status": "OK", "message": "Up and running"}


@app.get("/register", dependencies=[Depends(authorize)])
async def register(request: Request):
    tw = Twitter(TW_CONFIG)
    client_id = tw.get_client_id()
    redirect_uri = tw.get_redirect_uri()
    return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "client_id": client_id,
                "redirect_uri": redirect_uri
            }
        )


@app.get("/redirect", dependencies=[Depends(authorize)])
async def get_redirect(request: Request):
    params = {}
    for item in str(request.query_params).split("&"):
        key, value = item.split("=")
        params[key] = value
    print(params)
    tw = Twitter(TW_CONFIG)
    tw.get_access_token(params["code"])
    return {"status": "OK", "message": "Twitter configurate"}


@app.get("/update/")
async def update():
    yt_key = os.getenv("YT_KEY")
    yt_channel = os.getenv("YT_CHANNEL")
    youtube = YouTube(yt_key)
    db_video = Video.get_last_video_published()
    if db_video:
        yt_videos = youtube.get_videos(yt_channel, db_video.published_at)
        for yt_video in yt_videos:
            if yt_video['yt_id'] != db_video.yt_id:
                logger.info("Sin publicar")
                athread = Thread(target=populate, args=(yt_video,))
                athread.daemon = True
                athread.start()
                break
            else:
                populate_in_zs([{"status": "publicado", "data": yt_video}])
                logger.info("Publicado")
    else:
        yt_videos = youtube.get_videos(yt_channel)
        for yt_video in yt_videos:
            Video.new(yt_video['title'],
                      yt_video['description'],
                      yt_video['yt_id'],
                      yt_video['link'],
                      yt_video['published_at'])
    return {"status": "OK", "message": "Update completed"}


@app.get("/videos/")
async def get_videos():
    videos = Video.select()
    return sorted(videos, key=lambda k: k.published_at)


def populate(yt_video):
    populate_in_zs([yt_video])
    origen = "/tmp/origen.mp4"
    destino = "/tmp/destino.mp4"
    thumbnail_file = "/tmp/thumbnail.jpg"
    clean(origen, destino, thumbnail_file)
    yt_id = yt_video["yt_id"]
    title = yt_video['title']
    description = yt_video["description"]
    link = yt_video['link']
    message = title + '\n\n'
    largo = 270 - len(message) - len(link)
    message += yt_video['description'][0:largo] + '...\n\n' + link
    message_discord = f"**{title}**\n"
    message_discord += yt_video["description"] + "\n" + link
    message_mastodon = f"{title}\n{description}"
    max_length = 479 - len(link)
    if len(message_mastodon) > max_length:
        message_mastodon = message_mastodon[:max_length]
    message_mastodon = f"{message_mastodon}\n#atareaoConLinux\n{link}"

    try:
        download(yt_id)
        download_thumbnail(yt_id)
    except Exception as exception:
        logger.error(exception)
        logger.info("Can not continue")
        return
    try:
        convert(origen, destino)
        logger.info("Start save YouTube video")
        Video.new(yt_video['title'],
                  yt_video['description'],
                  yt_video['yt_id'],
                  yt_video['link'],
                  yt_video['published_at'])
        logger.info("End save YouTube video")
    except Exception as exception:
        logger.error(exception)
        logger.info("Can not continue")
        return
    try:
        telegramea(message, destino)
    except Exception as exception:
        logger.error(exception)
    try:
        telegramea_al_grupo(message, destino)
    except Exception as exception:
        logger.error(exception)
    try:
        discordea(message_discord)
    except Exception as exception:
        logger.error(exception)
    try:
        toot(message_mastodon, destino, title, thumbnail_file)
    except Exception as exception:
        logger.error(exception)
    try:
        export2PeerTube(title, description, origen)
    except Exception as exception:
        logger.error(exception)
    try:
        tweet(message, destino)
    except Exception as exception:
        logger.error(exception)
    clean(origen, destino, thumbnail_file)


@retry(tries=3, delay=30, logger=logger)
def download(yt_id):
    logger.info("Start download")
    url = f"https://www.youtube.com/watch?v={yt_id}"
    ydl_opts = {"outtmpl": "/tmp/origen",
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                "retries": 5}
    logger.info("Start download")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    logger.info("End download")


@retry(tries=3, delay=30, logger=logger)
def download_thumbnail(yt_id):
    logger.info("Start download thumbnail")
    tmpl = "/tmp/thumbnail"
    src = f"{tmpl}.webp"
    dst = f"{tmpl}.jpg"
    url = f"https://www.youtube.com/watch?v={yt_id}"
    ydl_opts = {"outtmpl": tmpl,
                "writethumbnail": True,
                "skip_download": True,
                "retries": 5}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    if os.path.exists(src):
        logger.info("Start convert from webp to jpg")
        image = Image.open(src)
        image.save(dst)
        os.remove(src)
        logger.info("End convert from webp to jpg")
    logger.info("End download thumbail")


def convert(origen, destino):
    logger.info("Start cutting")
    ffmpeg = local['ffmpeg']
    ffmpeg["-y", "-ss", "0", "-to", "45", "-i", origen, "-c", "copy",
           destino]()
    logger.info("End cutting")


@retry(tries=3, delay=10, logger=logger)
def tweet(message, filename):
    logger.info("Start tweeting")
    client_id = os.getenv("TW_CLIENT_ID")
    client_secret = os.getenv("TW_CLIENT_SECRET")
    access_token = os.getenv("TW_ACCESS_TOKEN")
    refresh_token = os.getenv("TW_REFRESH_TOKEN")
    consumer_key = os.getenv("TW_CONSUMER_KEY")
    consumer_secret = os.getenv("TW_CONSUMER_SECRET")
    resource_owner_key = os.getenv("TW_RESOURCE_OWNER_KEY")
    resource_owner_secret = os.getenv("TW_RESOURCE_OWNER_TOKEN")
    tw = Twitter(client_id, client_secret, access_token, refresh_token,
                 consumer_key, consumer_secret, resource_owner_key,
                 resource_owner_secret)

    populate_in_zs([{"destination": "twitter", "message": message}])
    logger.info("End tweeting")


@retry(tries=3, delay=5, logger=logger)
def toot(message, filename, description, thumbnail):
    logger.info("Start message in Mastodon")
    base_uri = os.getenv("MASTODON_BASE_URI")
    access_token = os.getenv("MASTODON_ACCESS_TOKEN")
    mastodon_client = MastodonClient(base_uri, access_token)
    mastodon_client.toot_with_media2(message, filename, description, thumbnail)
    populate_in_zs([{"destination": "mastodon", "message": message}])
    logger.info("End message in Mastodon")


@retry(tries=3, delay=5, logger=logger)
def discordea(message):
    logger.info("Start message in Discord")
    channel = os.getenv("DISCORD_CHANNEL")
    token = os.getenv("DISCORD_TOKEN")
    url = f"https://discord.com/api/webhooks/{channel}/{token}"
    data = {"content": message}
    requests.post(url, data)
    populate_in_zs([{"destination": "discord", "message": message}])
    logger.info("End message in Discord")


@retry(tries=3, delay=5, logger=logger)
def telegramea(message, filename):
    logger.info("Start message in Telegram")
    chat_id = os.getenv("TELEGRAM_CHANNEL")
    token = os.getenv("TELEGRAM_TOKEN")
    data = {"chat_id": chat_id, "caption": message}
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    with open(filename, "rb") as fr:
        requests.post(url, data=data, files={"video": fr})
        populate_in_zs([{"destination": "telegram", "data": data,
                        "message": message}])
    logger.info("End message in Telegram")


@retry(tries=3, delay=5, logger=logger)
def telegramea_al_grupo(message, filename):
    logger.info("Start message in Telegram to the group")
    group = os.getenv("TELEGRAM_GROUP")
    token = os.getenv("TELEGRAM_TOKEN")
    if group is not None and group.find(","):
        group_id, theme_id = group.split(",")
        data = {"chat_id": group_id,
                "caption": message,
                "message_thread_id": theme_id}
    else:
        data = {"chat_id": group,
                "caption": message}
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    with open(filename, "rb") as fr:
        requests.post(url, data=data, files={"video": fr})
        populate_in_zs([{"destination": "telegram", "data": data,
                        "message": message}])
    logger.info("End message in Telegram")


@retry(tries=3, delay=60, logger=logger)
def export2PeerTube(title, description, filename):
    logger.info("Start export to PeerTube")
    pt_path = os.getenv("PT_PATH")
    channel_id = os.getenv('PT_CHANNEL_ID')
    peerTube = PeerTube(pt_path)
    response = peerTube.upload(channel_id, filename, title, description)
    logger.info(response)
    populate_in_zs([{"destination": "peertube", "data": channel_id,
                    "title": title, "description": description}])
    logger.info("End export to PeerTube")


def clean(origen, destino, thumbnail_file):
    if os.path.exists(origen):
        os.remove(origen)
    if os.path.exists(destino):
        os.remove(destino)
    if os.path.exists(thumbnail_file):
        os.remove(thumbnail_file)


if __name__ == "__main__":
    yt_id = "ZZzJhyQHN70"
    download_thumbnail(yt_id)
