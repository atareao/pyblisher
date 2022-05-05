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

import requests
from utils import Log

URL = 'https://www.googleapis.com/youtube/v3'
YTURL = 'https://www.youtube.com'


class YouTube:

    def __init__(self, key):
        self.__key = key
        print(f"Key: {key}")

    def get_videos(self, channel_id, published_after=None, next_token=None):
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
                print(item)
                video_id = item['id']['videoId']
                link = f"{YTURL}/watch?v={video_id}"
                video = {"title": item['snippet']['title'],
                         "description": item['snippet']['description'],
                         "yt_id": video_id,
                         "link": link,
                         "published_at": item['snippet']['publishedAt']}
                videos.append(video)
            if 'nextPageToken' in data and data['nextPageToken']:
                more_videos = self.get_videos(channel_id,
                                              published_after,
                                              data['nextPageToken'])
                videos += more_videos
        else:
            Log.error(response.status_code)
            Log.error(response.text)
        return videos

    def get_channels(self, for_user_name, next_token=None):
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
            print(data)
        else:
            Log.error(response.status_code)
            Log.error(response.text)
        return channels

    def get_videos_from_list(self, playlist_id, next_token=None,
                             reverse_list=False):
        videos = []
        url = (f"{URL}/playlistItems?part=snippet&maxResults=50"
               f"&playlistId={playlist_id}&key={self.__key}")
        if next_token:
            url += f"&pageToken={next_token}"
        Log.info(url)
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
                video = {"title": item['snippet']['title'],
                         "description": item['snippet']['description'],
                         "yt_id": video_id,
                         "position": item['snippet']['position'],
                         "download_link": download_link,
                         "link": link,
                         "published": False}
                Log.debug(video)
                videos.append(video)
            if 'nextPageToken' in data and data['nextPageToken']:
                more_videos = self.get_videos_from_list(playlist_id,
                                                        data['nextPageToken'],
                                                        reverse_list)
                videos += more_videos
        else:
            Log.error(response.status_code)
            Log.error(response.text)
        Log.info(f"Reverse: {reverse_list}")
        videos = sorted(videos, key=lambda k: k['position'],
                        reverse=reverse_list)
        return videos

    def get_playlists(self, channel_id, next_token=None):
        playlists = []
        url = (f"{URL}/playlists?part=snippet&maxResults=50"
               f"&channelId={channel_id}&key={self.__key}")
        if next_token:
            url += f"&pageToken={next_token}"
        response = requests.get(url=url)
        if response.status_code == 200:
            data = response.json()
            for item in data['items']:
                playlist = {"yt_id": item['id'],
                            "title": item["snippet"]["title"],
                            "reverse": False}
                Log.debug(playlist)
                playlists.append(playlist)
            if 'nextPageToken' in data and data['nextPageToken']:
                more_playlists = self.get_playlists(channel_id,
                                                    data['nextPageToken'])
                playlists += more_playlists
        else:
            Log.error(response.status_code)
            Log.error(response.text)
        return playlists


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    yt_key = os.getenv('YT_KEY')
    channel_id = os.getenv('YT_CHANNEL')
    youtube = YouTube(yt_key)
    videos = youtube.get_videos(channel_id)
    print(videos)
