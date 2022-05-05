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
from mastodon import Mastodon


Table.DATABASE = "/app/database.db"
Log.LEVEL = Log.DEBUG

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
                print("Sin publicar")
                athread = Thread(target=populate, args=(yt_video,))
                athread.daemon = True
                athread.start()
                break
            else:
                print("Publicado")
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
    try:
        yt_id = yt_video["yt_id"]
        title = yt_video['title']
        link = yt_video['link']
        message = title + '\n\n'
        largo = 270 - len(message) - len(link)
        message += yt_video['description'][0:largo] + '...\n\n' + link
        message_discord = "**" + title + "**\n"
        message_discord += yt_video["description"] + "\n" + link
        url = f"https://www.youtube.com/watch?v={yt_id}"
        ydl_opts = {"outtmpl": "/tmp/origen",
                    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                    "retries": 5}
        print("Start download")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("End download")
        convert(origen, destino)
        tweet(message, destino)
        print("Start save YouTube video")
        Video.new(yt_video['title'],
                  yt_video['description'],
                  yt_video['yt_id'],
                  yt_video['link'],
                  yt_video['published_at'])
        print("End save YouTube video")
        telegramea(message, destino)
        discordea(message_discord)
        toot(message, destino)
    except Exception as exception:
        print(exception)
        print("Can not download")
    clean(origen, destino)


def convert(origen, destino):
    print("Start cutting")
    ffmpeg = local['ffmpeg']
    ffmpeg["-y", "-ss", "0", "-to", "45", "-i", origen, "-c", "copy",
           destino]()
    print("End cutting")


def tweet(message, filename):
    print("Start tweeting")
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
    print("End tweeting")


def toot(message, filename):
    print("Start message in Mastodon")
    access_token = os.getenv("MASTODON_ACCESS_TOKEN")
    print(access_token)
    base_url = os.getenv("MASTODON_BASE_URL")
    print(base_url)
    mastodon_client = Mastodon('/mastodon_user.secret',
                               'https://mastodon.social')
    print(str(mastodon_client))
    ans1 = mastodon_client.status_post("Status")
    print(str(ans1))
    ans = mastodon_client.media_post(filename, 'video/mp4')
    print("Salida:")
    print(str(ans))
    mastodon_client.status_post(message, media_ids=ans['id'])
    print("End message in Mastodon")


def discordea(message):
    print("Start message in Discord")
    channel = os.getenv("DISCORD_CHANNEL")
    token = os.getenv("DISCORD_TOKEN")
    url = f"https://discord.com/api/webhooks/{channel}/{token}"
    data = {"content": message}
    requests.post(url, data)
    print("End message in Discord")


def telegramea(message, filename):
    print("Start message in Telegram")
    chat_id = os.getenv("TELEGRAM_CHANNEL")
    token = os.getenv("TELEGRAM_TOKEN")
    data = {"chat_id": chat_id, "caption": message}
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    with open(filename, "rb") as fr:
        requests.post(url, data=data, files={"video": fr})
    print("End message in Telegram")


def clean(origen, destino):
    if os.path.exists(origen):
        os.remove(origen)
    if os.path.exists(destino):
        os.remove(destino)
