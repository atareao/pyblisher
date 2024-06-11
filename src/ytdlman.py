#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2023 Lorenzo Carbonell <a.k.a. atareao>

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


import json
import logging
import os
import yt_dlp
from plumbum import local
from datetime import datetime
from PIL import Image
from retry import retry


logger = logging.getLogger(__name__)


class YtDlMan:

    @staticmethod
    def self_update():
        logger.info("self_update")
        pip = local["pip"]
        output = pip["install", "--upgrade", "yt-dlp"]()
    @staticmethod
    @retry(tries=3, delay=30, logger=logger)
    def download(yt_id):
        logger.info("download")
        url = f"https://www.youtube.com/watch?v={yt_id}"
        ydl_opts = {"outtmpl": "/tmp/origen",
                    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                    "retries": 5,
                    "cookiefile": "/app/cookies.txt"}
        logger.info("Start download")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    @staticmethod
    @retry(tries=3, delay=30, logger=logger)
    def download_thumbnail(yt_id):
        logger.info("download_thumbnail")
        tmpl = "/tmp/thumbnail"
        src = f"{tmpl}.webp"
        dst = f"{tmpl}.jpg"
        url = f"https://www.youtube.com/watch?v={yt_id}"
        ydl_opts = {"outtmpl": tmpl,
                    "writethumbnail": True,
                    "skip_download": True,
                    "retries": 5,
                    "cookiefile": "/app/cookies.txt"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        if os.path.exists(src):
            logger.info("Start convert from webp to jpg")
            image = Image.open(src)
            image.save(dst)
            os.remove(src)
            logger.info("End convert from webp to jpg")

    @staticmethod
    @retry(tries=3, delay=30, logger=logger)
    def get_videos(yt_channel, published_at="1970-01-01T00:00:00Z"):
        logger.debug(f"channel: {yt_channel} and published_at: {published_at}")
        cookies = os.getenv("COOKIES")
        logger.debug(f"cookies: {cookies}")
        published_at = datetime\
                .strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")\
                .strftime("%Y%m%d")
        logger.info(f"Search videos at: {published_at}")
        videos = []
        url = f"https://www.youtube.com/channel/{yt_channel}"
        yt_dlp_bin = local["yt-dlp"]
        p = yt_dlp_bin.popen(["--dateafter", published_at, "--dump-json",
                            "--break-on-reject", "--cookies", cookies, url])
        p.wait()
        output, err = p.communicate()
        logger.debug(f"Output: {output}")
        for item in output.split("\n"):
            if item:
                item = json.loads(item)
                ts = datetime.strptime(item["upload_date"], "%Y%m%d")
                video = {
                    "title": item["title"],
                    "description": item["description"],
                    "thumbnail": item["thumbnail"],
                    "yt_id": item["id"],
                    "link": item["original_url"],
                    "published_at": ts.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                videos.append(video)
        return sorted(videos, key=lambda k: k["published_at"])
