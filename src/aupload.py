#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2021 Lorenzo Carbonell <a.k.a. atareao>

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


import argparse
import json
import logging
import os
import sys
import time

import requests
from requests_oauthlib import OAuth1

logger = logging.getLogger(__name__)

MEDIA_ENDPOINT_URL = "https://upload.twitter.com/1.1/media/upload.json"
POST_TWEET_URL = "https://api.twitter.com/1.1/statuses/update.json"


class ImageTweet(object):
    def __init__(self, oauth, status_text, file_name):
        """
        __init__(self, oauth, status_text, file_name)
            Initializes the object with the provided parameters.

            Args:
                oauth (object): The OAuth token or other authentication information.
                status_text (str): A text description of the image's processing status.
                file_name (str): The name of the file containing the image data.

            Attributes:
                image_filename (str): The name of the file containing the image data.
                total_bytes (int): The total size in bytes of the image file.
                media_id (None or int): A unique identifier for the processed media item, or None if not yet processed.
                processing_info (None or dict): Additional information about the processing status, or None if not yet processed.
                status_text (str): The text description of the image's processing status.

            Raises:
                None
        """
        self.image_filename = file_name
        self.total_bytes = os.path.getsize(self.image_filename)
        self.media_id = None
        self.processing_info = None
        self.status_text = status_text
        self.oauth = oauth

    def upload_init(self):
        """
        INIT: Initialize the media upload.

        Sends a POST request to the MEDIA_ENDPOINT_URL with the required data and authenticates using self.oauth.
        Extracts the media_id from the response JSON and assigns it to self.media_id.

        Args:
            self (object): The instance of the class this method is part of.
        """
        logger.info("INIT")

        request_data = {
            "command": "INIT",
            "media_type": "image/png",
            "total_bytes": self.total_bytes,
            "media_category": "tweet_image",
        }

        req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=self.oauth)
        media_id = req.json()["media_id"]

        self.media_id = media_id

        logger.info("Media ID: %s" % str(media_id))

    def upload_append(self):
        """
        Uploads media in chunks and appends to chunks uploaded
        """
        segment_id = 0
        bytes_sent = 0
        file = open(self.image_filename, "rb")

        while bytes_sent < self.total_bytes:
            chunk = file.read(4 * 1024 * 1024)

            logger.info("APPEND")

            request_data = {"command": "APPEND", "media_id": self.media_id, "segment_index": segment_id}

            files = {"media": chunk}

            req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, files=files, auth=self.oauth)

            if req.status_code < 200 or req.status_code > 299:
                logger.info(req.status_code)
                logger.info(req.text)
                sys.exit(0)

            segment_id = segment_id + 1
            bytes_sent = file.tell()

            logger.info(f"{bytes_sent} of {self.total_bytes} bytes uploaded")

        logger.info("Upload chunks complete.")

    def upload_finalize(self):
        """
        Finalizes uploads and starts video processing
        """
        logger.info("FINALIZE")

        request_data = {"command": "FINALIZE", "media_id": self.media_id}

        req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=self.oauth)
        logger.debug(req.json())

        self.processing_info = req.json().get("processing_info", None)
        self.check_status()

    def check_status(self):
        """
        Checks video processing status
        """
        if self.processing_info is None:
            return

        state = self.processing_info["state"]

        logger.info("Media processing status is %s " % state)

        if state == "succeeded":
            return

        if state == "failed":
            sys.exit(0)

        check_after_secs = self.processing_info["check_after_secs"]

        logger.info("Checking after %s seconds" % str(check_after_secs))
        time.sleep(check_after_secs)

        logger.info("STATUS")

        request_params = {"command": "STATUS", "media_id": self.media_id}

        req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params, auth=self.oauth)

        self.processing_info = req.json().get("processing_info", None)
        self.check_status()

    def tweet(self):
        """
        Publishes Tweet with attached image
        """
        request_data = {"status": self.status_text, "media_ids": self.media_id}

        req = requests.post(url=POST_TWEET_URL, data=request_data, auth=self.oauth)
        logger.debug(req.json())


class VideoTweet(object):
    def __init__(self, oauth, status_text, file_name):
        """
        Defines video tweet properties
        """
        self.video_filename = file_name
        self.total_bytes = os.path.getsize(self.video_filename)
        self.media_id = None
        self.processing_info = None
        self.status_text = status_text
        self.oauth = oauth

    def upload_init(self):
        """
        Initializes Upload
        """
        logger.info("INIT")

        request_data = {
            "command": "INIT",
            "media_type": "video/mp4",
            "total_bytes": self.total_bytes,
            "media_category": "tweet_video",
        }

        req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=self.oauth)
        media_id = req.json()["media_id"]

        self.media_id = media_id

        logger.info("Media ID: %s" % str(media_id))

    def upload_append(self):
        """
        Uploads media in chunks and appends to chunks uploaded
        """
        segment_id = 0
        bytes_sent = 0
        file = open(self.video_filename, "rb")

        while bytes_sent < self.total_bytes:
            chunk = file.read(4 * 1024 * 1024)

            logger.info("APPEND")

            request_data = {"command": "APPEND", "media_id": self.media_id, "segment_index": segment_id}

            files = {"media": chunk}

            req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, files=files, auth=self.oauth)

            if req.status_code < 200 or req.status_code > 299:
                logger.debug(req.status_code)
                logger.debug(req.text)
                sys.exit(0)

            segment_id = segment_id + 1
            bytes_sent = file.tell()

            logger.info(f"{bytes_sent} of {self.total_bytes} bytes uploaded")

        logger.info("Upload chunks complete.")

    def upload_finalize(self):
        """
        Finalizes uploads and starts video processing
        """
        logger.info("FINALIZE")

        request_data = {"command": "FINALIZE", "media_id": self.media_id}

        req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=self.oauth)
        logger.debug(req.json())

        self.processing_info = req.json().get("processing_info", None)
        self.check_status()

    def check_status(self):
        """
        Checks video processing status
        """
        if self.processing_info is None:
            return

        state = self.processing_info["state"]

        logger.info("Media processing status is %s " % state)

        if state == "succeeded":
            return

        if state == "failed":
            sys.exit(0)

        check_after_secs = self.processing_info["check_after_secs"]

        logger.info("Checking after %s seconds" % str(check_after_secs))
        time.sleep(check_after_secs)

        logger.info("STATUS")

        request_params = {"command": "STATUS", "media_id": self.media_id}

        req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params, auth=self.oauth)

        self.processing_info = req.json().get("processing_info", None)
        self.check_status()

    def tweet(self):
        """
        Publishes Tweet with attached video
        """
        request_data = {"status": self.status_text, "media_ids": self.media_id}

        req = requests.post(url=POST_TWEET_URL, data=request_data, auth=self.oauth)
        logger.debug(req.json())


def post_tweet(oauth, message):
    request_data = {"status": message}
    req = requests.post(url=POST_TWEET_URL, data=request_data, auth=oauth)
    logger.debug(req.json)


if __name__ == "__main__":
    config_file = os.path.join(os.path.expanduser("~"), ".config", "twitter", "config.json")
    parser = argparse.ArgumentParser(description="Send video to twitter")
    parser.add_argument("--message", required=True)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    with open(config_file) as fr:
        data = json.load(fr)
        consumer_key = data["consumer_key"]
        consumer_secret = data["consumer_secret"]
        access_token = data["access_token"]
        access_token_secret = data["access_token_secret"]
        status_text = args.message
        file_name = args.file
        oauth = OAuth1(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        # video_tweet = VideoTweet(oauth, status_text, file_name)
        # video_tweet.upload_init()
        # video_tweet.upload_append()
        # video_tweet.upload_finalize()
        # video_tweet.tweet()
        video_tweet = ImageTweet(oauth, status_text, file_name)
        video_tweet.upload_init()
        video_tweet.upload_append()
        video_tweet.upload_finalize()
