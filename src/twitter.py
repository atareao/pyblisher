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
import requests
import sys
import time
import urllib.parse
from pprint import pprint
from base64 import b64encode
import logging
import json
from requests_oauthlib import OAuth1

BASE_URI = "https://api.twitter.com"
MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'

logger = logging.getLogger(__name__)


class Twitter:
    def __init__(self, config_file):
        self._config_file = config_file
        self._load()

    def _load(self):
        with open(self._config_file, "r") as fr:
            self._config = json.load(fr)
            client_id = self._config["client_id"]
            client_secret = self._config["client_secret"]
            access_token = self._config["access_token"]
            refresh_token = self._config["refresh_token"]
            consumer_key = self._config["consumer_key"]
            consumer_secret = self._config["consumer_secret"]
            resource_owner_key = self._config["resource_owner_key"]
            resource_owner_secret = self._config["resource_owner_secret"]
            redirect_uri = self._config["redirect_uri"]

            self._basic_auth = b64encode(
                    f"{client_id}:{client_secret}".encode("utf-8")).decode()
            self._client_id = client_id
            self._access_token = access_token
            self._refresh_token = refresh_token
            self._oauth = OAuth1(consumer_key, client_secret=consumer_secret,
                                 resource_owner_key=resource_owner_key,
                                 resource_owner_secret=resource_owner_secret)
            self._redirect_uri = redirect_uri

    def _save(self):
        with open(self._config_file, "w") as fw:
            json.dump(self._config, fw)

    def get_client_id(self):
        return self._client_id

    def get_access_token(self, code):
        url = f"{BASE_URI}/2/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self._basic_auth}"
        }
        data = {
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self._redirect_uri,
            "code_verifier": "challenge"
            }
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            new_data = response.json()
            self._access_token = new_data["access_token"]
            self._refresh_token = new_data["refresh_token"]
            self._save()

    def update_access_token(self):
        url = f"{BASE_URI}/2/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {self._basic_auth}"
        }
        payload = {
            "refresh_token": self._refresh_token,
            "grant_type": "refresh_token",
            "client_id": self._client_id
        }
        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code in [200, 201]:
            data = response.json()
            self._config["access_token"] = data["access_token"]
            self._config["refresh_token"] = data["refresh_token"]
            self._save()
            return
        message_error = f"Error {response.status_code}: {response.text}"
        raise Exception(message_error)

    def get_me(self):
        url =  f"{BASE_URI}/1.1/account/verify_credentials.json"
        response = requests.get(url=url, auth=self._oauth)
        if response.status_code == 200:
            data = response.json()
            pprint(data)
        else:
            pprint(response.status_code)
            pprint(response)

    def get_mentions(self):
        url = "https://api.twitter.com/2/tweets/search/recent?query=from:TwitterDev&tweet.fields=created_at&expansions=author_id&user.fields=created_at"
        response = requests.get(url=url, auth=self._oauth)
        if response.status_code == 200:
            data = response.json()
            pprint(data)
        else:
            pprint(response.status_code)
            pprint(response)
        

    def get_last_mentions(self, last_id=None):
        query = urllib.parse.quote("@atareao -filter:retweets")
        url = (f"{BASE_URI}/1.1/search/tweets.json?"
               f"q={query}&include_entities=false&result_type=recent")
        params = {
            "query": query
        }
        if last_id:
            params["since_id"] = last_id
        try:
            response = self._get(url, params)
            pprint(response)
        except Exception as exception:
            pprint(exception)

    def post(self, message):
        url = f"{BASE_URI}/2/tweets"
        payload = {"text": message}
        try:
            response = self._post(url, payload)
            logger.debug(response)
        except Exception as exception:
            logger.error(exception)

    def get_tweets(self):
        url = f"{BASE_URI}/2/tweets"
        try:
            response = self._get(url)
            logger.debug(response)
        except Exception as exception:
            logger.error(exception)

    def _post(self, url, payload):
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url=url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return response.json()
        message_error = f"Error {response.status_code}: {response.text}"
        raise Exception(message_error)

    def _get(self, url, params={}):
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json"
        }
        response = requests.post(url=url, headers=headers, params=params)
        if response.status_code in [200, 201]:
            return response.json()
        message_error = f"Error {response.status_code}: {response.text}"
        raise Exception(message_error)

    def get_last_tweet(self, user_id, last_id):
        url = (f"{BASE_URI}/1.1/statuses/user_timeline.json?"
               f"user_id={user_id}&since_id={last_id}&count=1")
        response = requests.get(url=url, auth=self._oauth1)
        if response.status_code == 200:
            data = response.json()
            pprint(data)
        else:
            pprint(response.status_code)

    def populate_video(self, text, filename):
        """
        Publishes Tweet with attached video
        """
        video_tweet = VideoTweet(self._oauth, filename)
        video_tweet.upload_init()
        video_tweet.upload_append()
        video_tweet.upload_finalize()
        if video_tweet.get_media_id() != None:
            url = f"{BASE_URI}/2/tweets"
            payload = {
                "text": text,
                "media": {
                    "media_ids": [video_tweet.get_media_id()]
                    }
            }
            try:
                response = self._post(url, payload)
                logger.debug(response)
            except Exception as exception:
                logger.error(exception)


class VideoTweet:

    def __init__(self, oauth, file_name):
        '''
        Defines video tweet properties
        '''
        self.video_filename = file_name
        self.total_bytes = os.path.getsize(self.video_filename)
        self.media_id = None
        self.processing_info = None
        self.oauth = oauth

    def get_media_id(self):
        return str(self.media_id)

    def upload_init(self):
        '''
        Initializes Upload
        '''
        logger.info('INIT')

        request_data = {
            'command': 'INIT',
            'media_type': 'video/mp4',
            'total_bytes': self.total_bytes,
            'media_category': 'tweet_video'
        }

        req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data,
                            auth=self.oauth)
        media_id = req.json()['media_id']

        self.media_id = media_id

        logger.info('Media ID: %s' % str(media_id))

    def upload_finalize(self):
        '''
        Finalizes uploads and starts video processing
        '''
        logger.info('FINALIZE')

        request_data = {
            'command': 'FINALIZE',
            'media_id': self.media_id
        }

        req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data,
                            auth=self.oauth)
        logger.debug(req.json())

        self.processing_info = req.json().get('processing_info', None)
        self.check_status()

    def check_status(self):
        '''
        Checks video processing status
        '''
        if self.processing_info is None:
            return

        state = self.processing_info['state']

        logger.info('Media processing status is %s ' % state)

        if state == u'succeeded':
            return

        if state == u'failed':
            sys.exit(0)

        check_after_secs = self.processing_info['check_after_secs']

        logger.info('Checking after %s seconds' % str(check_after_secs))
        time.sleep(check_after_secs)

        logger.info('STATUS')

        request_params = {
            'command': 'STATUS',
            'media_id': self.media_id
        }

        req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params,
                           auth=self.oauth)

        self.processing_info = req.json().get('processing_info', None)
        self.check_status()

    def upload_append(self):
        '''
        Uploads media in chunks and appends to chunks uploaded
        '''
        segment_id = 0
        bytes_sent = 0
        file = open(self.video_filename, 'rb')

        while bytes_sent < self.total_bytes:
            chunk = file.read(4*1024*1024)

            logger.info('APPEND')

            request_data = {
                'command': 'APPEND',
                'media_id': self.media_id,
                'segment_index': segment_id
            }

            files = {
                'media': chunk
            }

            req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data,
                                files=files, auth=self.oauth)

            if req.status_code < 200 or req.status_code > 299:
                logger.debug(req.status_code)
                logger.debug(req.text)
                sys.exit(0)

            segment_id = segment_id + 1
            bytes_sent = file.tell()

            logger.info(f"{bytes_sent} of {self.total_bytes} bytes uploaded")

        logger.info('Upload chunks complete.')
