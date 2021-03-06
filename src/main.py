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
from dotenv import load_dotenv
from fastapi import FastAPI
from video import Video
from table import Table
from utils import Log
from ytapi import YouTube
from threading import Thread
from plumbum import local
from requests_oauthlib import OAuth1
from aupload import VideoTweet
from mastodonapi import MastodonClient
from fdapi import PeerTube
from retry import retry

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
Table.DATABASE = "/app/database.db"
Log.LEVEL = Log.DEBUG

logging.basicConfig(stream=sys.stdout,
                    filemode="w",
                    format=LOG_FORMAT,
                    level=logging.INFO)

logger = logging.getLogger()

load_dotenv()
Video.inicializate()
app = FastAPI()


@app.get("/status/")
async def status():
    return {"status": "OK", "message": "Up and running"}


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
    origen = "/tmp/origen.mp4"
    destino = "/tmp/destino.mp4"
    clean(origen, destino)
    yt_id = yt_video["yt_id"]
    title = yt_video['title']
    description = yt_video["description"]
    link = yt_video['link']
    message = title + '\n\n'
    largo = 270 - len(message) - len(link)
    message += yt_video['description'][0:largo] + '...\n\n' + link
    message_discord = "**" + title + "**\n"
    message_discord += yt_video["description"] + "\n" + link
    message_mastodon = f"{title}\n\n{description}"
    max_length = 495 - len(link)
    if len(message_mastodon) > max_length:
        message_mastodon = message_mastodon[:max_length]
    message_mastodon = f"{message_mastodon}\n\n{link}"

    try:
        download(yt_id)
    except Exception as exception:
        logger.error(exception)
        logger.info("Can not continue")
        return
    try:
        convert(origen, destino)
        tweet(message, destino)
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
        discordea(message_discord)
    except Exception as exception:
        logger.error(exception)
    try:
        toot(message_mastodon, destino)
    except Exception as exception:
        logger.error(exception)
    try:
        export2PeerTube(title, description, origen)
    except Exception as exception:
        logger.error(exception)
    clean(origen, destino)


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


def convert(origen, destino):
    logger.info("Start cutting")
    ffmpeg = local['ffmpeg']
    ffmpeg["-y", "-ss", "0", "-to", "45", "-i", origen, "-c", "copy",
           destino]()
    logger.info("End cutting")


@retry(tries=3, delay=10, logger=logger)
def tweet(message, filename):
    logger.info("Start tweeting")
    consumer_key = os.getenv("TW_CONSUMER_KEY")
    consumer_secret = os.getenv("TW_CONSUMER_SECRET")
    access_token = os.getenv("TW_ACCESS_TOKEN")
    access_token_secret = os.getenv("TW_ACCESS_TOKEN_SECRET")
    oauth = OAuth1(consumer_key, client_secret=consumer_secret,
                   resource_owner_key=access_token,
                   resource_owner_secret=access_token_secret)
    video_tweet = VideoTweet(oauth, message, filename)
    video_tweet.upload_init()
    video_tweet.upload_append()
    video_tweet.upload_finalize()
    video_tweet.tweet()
    logger.info("End tweeting")


@retry(tries=3, delay=5, logger=logger)
def toot(message, filename):
    logger.info("Start message in Mastodon")
    base_uri = os.getenv("MASTODON_BASE_URI")
    access_token = os.getenv("MASTODON_ACCESS_TOKEN")
    mastodon_client = MastodonClient(base_uri, access_token)
    mastodon_client.toot_with_media(message, filename)
    logger.info("End message in Mastodon")


@retry(tries=3, delay=5, logger=logger)
def discordea(message):
    logger.info("Start message in Discord")
    channel = os.getenv("DISCORD_CHANNEL")
    token = os.getenv("DISCORD_TOKEN")
    url = f"https://discord.com/api/webhooks/{channel}/{token}"
    data = {"content": message}
    requests.post(url, data)
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
    logger.info("End message in Telegram")


@retry(tries=3, delay=60, logger=logger)
def export2PeerTube(title, description, filename):
    logger.info("Start export to PeerTube")
    pt_path = os.getenv("PT_PATH")
    channel_id = os.getenv('PT_CHANNEL_ID')
    peerTube = PeerTube(pt_path)
    response = peerTube.upload(channel_id, filename, title, description)
    logger.info(response)
    logger.info("End export to PeerTube")


def clean(origen, destino):
    if os.path.exists(origen):
        os.remove(origen)
    if os.path.exists(destino):
        os.remove(destino)
