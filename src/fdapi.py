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
import time
import mimetypes
import requests
import toml
import logging

logger = logging.getLogger(__name__)

mimetypes.init()


class PeerTube:
    def __init__(self, path):
        self.path = path
        self.conf = self.__read_configuration()
        self.login()
        # self.logout()

    def get_user_info(self):
        base_url = self.conf['credentials']['base_url']
        url = f"{base_url}/users/me"
        token_type = self.conf['token']['token_type']
        access_token = self.conf['token']['access_token']
        headers = {
                "Authorization": f"{token_type} {access_token}",
                }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return {}

    def list_videos(self, name):
        base_url = self.conf['credentials']['base_url']
        url = f"{base_url}/accounts/{name}/videos"
        logger.debug(f"Url: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        print(response.status_code)
        print(response.text)
        return []

    def upload(self, channel_id, filepath, name, description,
               privace_policy_id=1, license_id=1, language='es',
               category_id=15):
        """
        url: https://docs.joinpeertube.org/api-rest-reference.html#operation/
            uploadLegacy
        Privacy Policies:
            "1": "Public",
            "2": "Unlisted",
            "3": "Private",
            "4": "Internal"
        Licenses:
            "1": "Attribution",
            "2": "Attribution - Share Alike",
            "3": "Attribution - No Derivatives",
            "4": "Attribution - Non Commercial",
            "5": "Attribution - Non Commercial - Share Alike",
            "6": "Attribution - Non Commercial - No Derivatives",
            "7": "Public Domain Dedication"
        Languages:
            "es": "Spanish",
            "en": "English"
        Categories:
            "1": "Music",
            "2": "Films",
            "3": "Vehicles",
            "4": "Art",
            "5": "Sports",
            "6": "Travels",
            "7": "Gaming",
            "8": "People",
            "9": "Comedy",
            "10": "Entertainment",
            "11": "News & Politics",
            "12": "How To",
            "13": "Education",
            "14": "Activism",
            "15": "Science & Technology",
            "16": "Animals",
            "17": "Kids",
            "18": "Food"
        """
        base_url = self.conf['credentials']['base_url']
        url = f"{base_url}/videos/upload"
        token_type = self.conf['token']['token_type']
        access_token = self.conf['token']['access_token']
        headers = {
                "Authorization": f"{token_type} {access_token}",
                }
        data = {
                "channelId": channel_id,
                "name": name,
                "description": description,
                "category": category_id,
                "language": language,
                "license": license_id,
                "privacy": privace_policy_id
                }
        logger.debug(data)
        filename = os.path.basename(filepath)
        mimetype = mimetypes.guess_type(filepath)[0]
        logger.info(f"Going to upload {filepath} with mimetype {mimetype}")
        with open(filepath, 'rb') as file_reader:
            files = {"videofile": (filename, file_reader, mimetype)}
            response = requests.post(url, headers=headers, data=data,
                                     files=files)
            logger.debug(response.status_code)
            logger.debug(response.content)
            if response.status_code == 200:
                return True
            logger.error(f"Can't download {filepath}")
        return False

    def get_metadata_video_file(self, uuid):
        base_url = self.conf['credentials']['base_url']
        url = f"{base_url}/videos/{uuid}/source"
        print(url)
        token_type = self.conf['token']['token_type']
        access_token = self.conf['token']['access_token']
        headers = {
                "Authorization": f"{token_type} {access_token}",
                }
        response = requests.get(url, headers=headers)
        return response

    def download_video_file(self, filename):
        base_url = self.conf['credentials']['base_url']
        url = f"https://fediverse.tv/static/web-videos/{filename}"
        print(url)
        token_type = self.conf['token']['token_type']
        access_token = self.conf['token']['access_token']
        headers = {
                "Authorization": f"{token_type} {access_token}",
                }
        response = requests.get(url, headers=headers)
        return response


    def logout(self):
        base_url = self.conf['credentials']['base_url']
        url = f"{base_url}/users/revoke-token"
        token_type = self.conf['token']['token_type']
        access_token = self.conf['token']['access_token']
        headers = {
                "Authorization": f"{token_type} {access_token}",
                }
        try:
            requests.post(url, headers=headers)
        finally:
            self.conf['token']['expires_in'] = 0
            self.conf['token']['refresh_token_expires_in'] = 0
            self.__save_conf()
            logger.info("===")

    def login(self):
        if self.conf['client']['client_id'] == "" or \
                self.conf['client']['client_secret'] == "":
            self.__login_prerequisite()
        timestamp = int(time.time())
        if self.conf['token']['token_type'] == '' or \
                self.conf['token']['access_token'] == '' or \
                self.conf['token']['access_token'] == '' or \
                timestamp > self.conf['token']['refresh_token_expires_in']:
            self.__get_access_token()
        elif timestamp > self.conf['token']['expires_in']:
            self.__get_refresh_token()

    def __read_configuration(self):
        conf = {}
        try:
            conf = toml.load(self.path)
        except Exception as exception:
            logger.error(exception)
        return conf

    def __login_prerequisite(self):
        base_url = self.conf['credentials']['base_url']
        url = f"{base_url}/oauth-clients/local"
        response = requests.get(url)
        if response.status_code == 200:
            self.conf['client'] = response.json()
            self.__save_conf()
        else:
            raise Exception

    def __get_access_token(self):
        client_id = self.conf['client']['client_id']
        client_secret = self.conf['client']['client_secret']
        base_url = self.conf['credentials']['base_url']
        username = self.conf['credentials']['username']
        password = self.conf['credentials']['password']
        url = f"{base_url}/users/token"
        data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "password",
                "response_type": "code",
                "username": username,
                "password": password
                }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            data = response.json()
            timestamp = int(time.time())
            data['expires_in'] += timestamp
            data['refresh_token_expires_in'] += timestamp
            self.conf['token'] = data
            self.__save_conf()
        else:
            raise Exception

    def __get_refresh_token(self):
        base_url = self.conf['credentials']['base_url']
        client_id = self.conf['client']['client_id']
        client_secret = self.conf['client']['client_secret']
        refresh_token = self.conf['token']['refresh_token']
        url = f"{base_url}/users/token"
        data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
                }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            data = response.json()
            timestamp = int(time.time())
            data['expires_in'] += timestamp
            data['refresh_token_expires_in'] += timestamp
            self.conf['token'] = data
            self.__save_conf()
        else:
            logger.debug(response.status_code)
            self.conf['token']['refresh_token_expires_in'] = 0
            self.__save_conf()

    def __save_conf(self):
        with open(self.path, 'w') as file_writer:
            toml.dump(self.conf, file_writer)


if __name__ == '__main__':
    from pprint import pprint
    from dotenv import load_dotenv
    load_dotenv()
    pt_path = os.getenv("PT_PATH")
    peerTube = PeerTube(pt_path)
    data = peerTube.get_user_info()
    print(data)
    channel_id = os.getenv('PT_CHANNEL_ID')
    name = "test"
    filepath = "cap5.mp4"
    # response = peerTube.upload(channel_id, name, filepath)
    response = peerTube.list_videos("atareaouser")
    pprint(response)
    info = peerTube.get_metadata_video_file("9bd10e18-218b-491f-921f-a850412f8d90")
    pprint(info.status_code)
    pprint(info.text)
    # info = peerTube.download_video_file("9bd10e18-218b-491f-921f-a850412f8d90")
    # pprint(info.status_code)
    # pprint(info.text)
