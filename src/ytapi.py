
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
import requests

logger = logging.getLogger(__name__)

URL = 'https://www.googleapis.com/youtube/v3'
YTURL = 'https://www.youtube.com'


class YouTube:

    def __init__(self, key):
        self.__key = key

    def get_videos(self, channel_id, published_after=None, next_token=None):
        logger.debug(f"get_videos channel_id: {channel_id}, published_after: "
                     f"{published_after}, next_token: {next_token}")
        videos = []
        url = f"{URL}/search"
        params = {"part": "snippet",
                  "channelId": channel_id,
                  "maxResults": 50,
                  "order": "date",
                  "type": "video",
                  "key": self.__key}
        if published_after:
            params['publishedAfter'] = published_after
        if next_token:
            params["pageToken"] = next_token
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for item in data['items']:
                if item['snippet']['title'].lower() == 'private video' or \
                        item['snippet']['title'].lower() == 'deleted video':
                    continue
                logger.debug(item)
                video_id = item['id']['videoId']
                link = f"{YTURL}/watch?v={video_id}"
                snippet = self.get_snippet(video_id)
                snippet = snippet if snippet else item["snippet"]
                video = {
                    "title": snippet['title'],
                    "description": snippet['description'],
                    "thumbnail": snippet['thumbnails']['high']['url'],
                    "yt_id": video_id,
                    "link": link,
                    "published_at": snippet['publishedAt']}
                videos.append(video)
            if 'nextPageToken' in data and data['nextPageToken']:
                more_videos = self.get_videos(channel_id,
                                              published_after,
                                              data['nextPageToken'])
                videos += more_videos
        else:
            logger.error(response.status_code)
            logger.error(response.text)
        return videos

    def get_channels(self, for_user_name, next_token=None):
        logger.debug(f"get_channels for_user_name: {for_user_name}, "
                     f"next_token: {next_token}")
        channels = []
        url = f"{URL}/channels"
        params = {"part": "snippet",
                  "forUsername": for_user_name,
                  "maxResults": 50,
                  "key": self.__key}
        if next_token:
            params["pageToken"] = next_token
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            logger.debug(data)
        else:
            logger.error(response.status_code)
            logger.error(response.text)
        return channels

    def get_snippet(self, yt_id: str) -> dict | None:
        logger.debug(f"get_description for '{yt_id}'")
        url = f"{URL}/videos"
        params = {"part": "snippet",
                  "id": yt_id,
                  "key": self.__key}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if len(data["items"]) > 0:
                return data["items"][0]["snippet"]
        else:
            logger.error(response.status_code)
            logger.error(response.text)
            print(response.status_code)
            print(response.text)
        return None

    def get_videos_from_list(self, playlist_id, next_token=None,
                             reverse_list=False):
        logger.debug(f"get_videos_from_list playlist_id: {playlist_id}, "
                     f"next_token: {next_token}, reverse_list: {reverse_list}")
        videos = []
        url = (f"{URL}/playlistItems?part=snippet&maxResults=50"
               f"&playlistId={playlist_id}&key={self.__key}")
        if next_token:
            url += f"&pageToken={next_token}"
        logger.info(url)
        response = requests.get(url=url)
        if response.status_code == 200:
            data = response.json()
            for item in data['items']:
                if item['snippet']['title'].lower() == 'private video' or \
                        item['snippet']['title'].lower() == 'deleted video':
                    continue
                video_id = item['snippet']['resourceId']['videoId']
                link = f"{YTURL}/watch?v={video_id}&list={playlist_id}"
                download_link = f"{YTURL}/watch?v={video_id}"
                video = {
                    "title": item['snippet']['title'],
                    "description": item['snippet']['description'],
                    "thumbnail": item['snippet']['thumbnails']['high']['url'],
                    "yt_id": video_id,
                    "position": item['snippet']['position'],
                    "download_link": download_link,
                    "link": link,
                    "published_at": item["snippet"]["publishedAt"],
                    "published": False
                }
                logger.debug(video)
                videos.append(video)
            if 'nextPageToken' in data and data['nextPageToken']:
                more_videos = self.get_videos_from_list(playlist_id,
                                                        data['nextPageToken'],
                                                        reverse_list)
                videos += more_videos
        else:
            logger.error(response.status_code)
            logger.error(response.text)
        logger.info(f"Reverse: {reverse_list}")
        videos = sorted(videos, key=lambda k: k['position'],
                        reverse=reverse_list)
        return videos

    def get_playlists(self, channel_id, next_token=None):
        logger.debug(f"get_playlist channel_id: {channel_id}, "
                     f"next_token: {next_token}")
        playlists = []
        url = (f"{URL}/playlists?part=snippet&maxResults=50"
               f"&channelId={channel_id}&key={self.__key}")
        if next_token:
            url += f"&pageToken={next_token}"
        logger.debug(f"url: {url}")
        response = requests.get(url=url)
        if response.status_code == 200:
            data = response.json()
            for item in data['items']:
                playlist = {"yt_id": item['id'],
                            "title": item["snippet"]["title"],
                            "reverse": False}
                logger.debug(playlist)
                playlists.append(playlist)
            if 'nextPageToken' in data and data['nextPageToken']:
                more_playlists = self.get_playlists(channel_id,
                                                    data['nextPageToken'])
                playlists += more_playlists
        else:
            logger.error(response.status_code)
            logger.error(response.text)
        return playlists


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    yt_key = os.getenv('YT_KEY')
    channel_id = os.getenv('YT_CHANNEL')
    print(yt_key)
    print(channel_id)
    youtube = YouTube(yt_key)
    yt_videos = youtube.get_videos(channel_id,
                                   published_after="2024-07-07T16:00:01Z")
    for yt_video in yt_videos:
        print(yt_video)
        yt_id = yt_video["yt_id"]
        print(yt_id)
