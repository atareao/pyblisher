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


from fastapi import FastAPI, Body, Path
from video import Video
from lista import Lista
from schedule import Schedule
from table import Table
from utils import Log

Table.DATABASE = "database.db"
Log.LEVEL = Log.DEBUG

Video.inicializate()
Lista.inicializate()
Schedule.inicializate()
app = FastAPI()



@app.get("/schedule/")
async def get_schedule():
    return Schedule.get_all()

@app.get("/videos/")
async def get_videos_for_list(list_id=None, published=None):
    if list_id or published:
        conditions = []
        if list_id:
            conditions.append(f"list_id={list_id}")
        if published:
            conditions.append(f"published is {published}")
        return Video.select(conditions)

@app.post("/videos/")
async def create_video(yt_id: str = Body(...), list_id: str = Body(...),
        published: bool = Body(...)):
    db_video = Video.find_by_yt_id(yt_id)
    if db_video:
        return {"result": "KO", "msg": "Already exists"}
    return Video.new(yt_id, list_id, published)

@app.get("/listas/")
async def get_listas():
    return Lista.get_all()

@app.post("/listas/")
async def create_lista(yt_id: str = Body(...), title: str = Body(...),
        reverse: bool = Body(...)):
    db_lista = Lista.find_by_yt_id(yt_id)
    if db_lista:
        return {"result": "KO", "msg": "Already exists"}
    return Lista.new(yt_id, title, reverse)

