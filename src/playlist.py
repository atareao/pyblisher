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

class Playlist(Table):
    TABLE = 'Playlists'
    UNIKEYS = ['YT_ID']
    CREATE_TABLE_QUERY = (f"CREATE TABLE IF NOT EXISTS {TABLE}("
                          "ID INTEGER PRIMARY KEY AUTOINCREMENT, "
                          "YT_ID TEXT, "
                          "TITLE TEXT, "
                          "REVERSE BOOLEAN)")

    @classmethod
    def find_by_yt_id(cls, yt_id):
        items = cls.select(f"yt_id='{yt_id}'")
        if items:
            return items[0]
        return None

    @classmethod
    def new(cls, yt_id, title, reverse):
        playlist = Playlist.from_dict({"yt_id": yt_id, "title": title,
            "reverse": reverse})
        playlist.save()
        return playlist


