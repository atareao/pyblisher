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

import logging
from table import Table

logger = logging.getLogger(__name__)


class Video(Table):
    TABLE = 'VIDEOS'
    UNIKEYS = ['yt_id']
    CREATE_TABLE_QUERY = (f"CREATE TABLE IF NOT EXISTS {TABLE}("
                          "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "TITLE TEXT,"
                          "DESCRIPTION TEXT,"
                          "YT_ID TEXT,"
                          "LINK TEXT,"
                          "PUBLISHED_AT TEXT)")

    @classmethod
    def get_last_video_published(cls):
        """
        Returns the last video published.

        This method fetches all videos, sorts them by publication date
        (in descending order), and returns the first item in this sorted list.
        If no videos are found, None is returned.

        :return: The last video published, or None if no such video exists.
        """
        condition = "published_at IS NOT NULL ORDER BY published_at DESC"
        items = cls.select(condition)
        return items[0] if len(items) > 0 else None

    @classmethod
    def new(cls, title, description, yt_id, link, published_at):
        """
        Creates a new Video object and saves it to the database.

        Parameters:
        title (str): The title of the video.
        description (str): A brief description of the video.
        yt_id (str): The YouTube ID of the video.
        link (str): The URL link to the video.
        published_at (datetime): The date and time the video was published.

        Returns:
        A new Video object representing the newly created video in the database
        """
        video = Video.from_dict({"title": title,
                                 "description": description,
                                 "yt_id": yt_id,
                                 "link": link,
                                 "published_at": published_at})
        video.save()
        return video

    @classmethod
    def find_by_yt_id(cls, yt_id):
        """
        Finds a video by its YouTube ID.

        This method returns the first video found with the given YouTube ID.
        If no such video exists, None is returned.

        :param yt_id: The YouTube ID of the video to find.
        :return: A Video object representing the found video, or None if not
        found.
        """
        items = cls.select(f"yt_id='{yt_id}'")
        if items:
            return items[0]
        return None
