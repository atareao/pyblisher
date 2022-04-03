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
from dotenv import load_dotenv
from datetime import date, datetime
from fastapi import FastAPI, Body, Path
from video import Video
from playlist import Playlist
from schedule import Schedule
from table import Table
from utils import Log
from ytapi import YouTube


Table.DATABASE = "database.db"
Log.LEVEL = Log.DEBUG

load_dotenv()
Video.inicializate()
Playlist.inicializate()
Schedule.inicializate()
app = FastAPI()



@app.get("/schedule/")
async def get_schedule():
    return Schedule.get_all()

@app.get("/update/")
async def update():
    yt_key = os.getenv("YT_KEY")
    yt_channel = os.getenv("YT_CHANNEL")
    youtube = YouTube(yt_key)
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
    return {"status": "OK", "message": "Update completed"}


@app.get("/votd/")
async def get_votd():
    videos = []
    weekday = datetime.today().weekday()
    condition = f"day = {weekday} AND publish is TRUE"
    schedules = Schedule.select(condition)
    for schedule in schedules:
        condition = f"list_id={schedule.list_id} AND published is FALSE"
        some_videos = Video.select(condition)
        videos.extend(some_videos)
    return videos


@app.get("/videos/")
async def get_videos_for_list(playlist_id=None, published=None):
    conditions = []
    if playlist_id or published:
        if playlist_id:
            conditions.append(f"playlist_id={playlist_id}")
        if published:
            conditions.append(f"published is {published}")
    return sorted(Video.select(conditions), key=lambda k: k.position)

@app.post("/videos/")
async def create_video(yt_id: str = Body(...), playlist_id: str = Body(...),
        published: bool = Body(...)):
    db_video = Video.find_by_yt_id(yt_id)
    if db_video:
        return {"result": "KO", "msg": "Already exists"}
    return Video.new(yt_id, playlist_id, published)

@app.get("/playlists/")
async def get_playlists():
    return Playlist.get_all()

@app.post("/listas/")
async def create_playlist(yt_id: str = Body(...), title: str = Body(...),
        reverse: bool = Body(...)):
    db_lista = Playlist.find_by_yt_id(yt_id)
    if db_lista:
        return {"result": "KO", "msg": "Already exists"}
    return Playlist.new(yt_id, title, reverse)

