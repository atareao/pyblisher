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

from table import Table

class Video(Table):
    TABLE = 'VIDEOS'
    PK = 'id'
    UNIKEYS = ['yt_id']
    CREATE_TABLE_QUERY = (f"CREATE TABLE IF NOT EXISTS {TABLE}("
                          f"{PK} INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "YT_ID TEXT,"
                          "LIST_ID INTEGER,"
                          "PUBLISHED BOOLEAN)")

    @classmethod
    def get_first_video_not_published(cls, list_id, asc=True):
        condition = f"list_id='{list_id} ORDER BY ID "
        condition += "ASC" if asc is True else "DESC"
        items = cls.select(condition)
        return items[0] if len(items) > 0 else None


    @classmethod
    def new(cls, yt_id, list_id, published):
        video = Video.from_dict({"yt_id": yt_id, "list_id": list_id,
            "published": published})
        video.save()
        return video

    @classmethod
    def find_by_yt_id(cls, yt_id):
        condition = f"yt_id={yt_id}"
        return Video.select(condition)



