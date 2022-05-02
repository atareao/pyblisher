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
import yt_dlp
from dotenv import load_dotenv
from fastapi import FastAPI
from video import Video
from table import Table
from utils import Log
from ytapi import YouTube
from threading import Thread


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
            else:
                print("Publicado")
            athread = Thread(target=download, args=(yt_video['yt_id'],))
            athread.daemon = True
            athread.start()
            print(yt_video)
    else:
        yt_videos = youtube.get_videos(yt_channel)
        for yt_video in yt_videos:
            Video.new(yt_video['title'],
                      yt_video['description'],
                      yt_video['yt_id'],
                      yt_video['link'],
                      yt_video['published_at'])
    """
    playlists = youtube.get_playlists(yt_channel)
    for aplaylist in playlists:
        db_playlist = Playlist.find_by_yt_id(aplaylist['yt_id'])
        if not db_playlist:
            db_playlist = Playlist.from_dict(aplaylist)
            db_playlist.save()
        reverse_list = (db_playlist.reverse == 1)
        videos = youtube.get_videos(aplaylist['yt_id'],
                reverse_list=reverse_list)
        for avideo in videos:
            db_video = Video.find_by_yt_id(avideo['yt_id'])
            avideo['playlist_id'] = db_playlist.id
            if not db_video:
                db_video = Video.from_dict(avideo)
                db_video.save()
    """
    return {"status": "OK", "message": "Update completed"}


@app.get("/videos/")
async def get_videos():
    videos = Video.select()
    return sorted(videos, key=lambda k: k.published_at)


def download(code):
    try:
        origen = "/tmp/origen.mp4"
        destino = "/tmp/origen.mp4"
        if os.path.exists(origen):
            os.remove(origen)
        if os.path.exists(destino):
            os.remove(destino)
        url = f"https://www.youtube.com/watch?v={code}"
        ydl_opts = {"outtmpl": "/tmp/origen",
                    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                    "retries": 5,
                    "concurrent-fragments": 5,
                    "fragment-retries": 5}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download finished")
    except Exception as exception:
        print(exception)
        print("Can not download")
