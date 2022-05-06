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
from time import sleep

BASE_URI = "https://mastodon.social"


class MastodonClient:
    def __init__(self, base_uri, access_token):
        self.__base_uri = base_uri
        self.__headers = {"Authorization": f"Bearer {access_token}"}

    def test_credentials(self):
        url = f"{self.__base_uri}/api/v1/accounts/verify_credentials"
        try:
            response = requests.get(url, headers=self.__headers)
            if response.status_code == 200:
                return response.json()
            message = f"HTTP Code: {response.status_code}. {response.text}"
            raise Exception(message)
        except Exception as exception:
            print(exception)
        return None

    def toot(self, status, media_ids=[]):
        url = f"{self.__base_uri}/api/v1/statuses"
        try:
            data = {"status": status,
                    "media_ids": media_ids}
            response = requests.post(url, headers=self.__headers, json=data)
            if response.status_code == 200:
                return response.json()
            message = f"HTTP Code: {response.status_code}. {response.text}"
            raise Exception(message)
        except Exception as exception:
            print(exception)
        return None

    def upload_media(self, filename):
        print("upload_media")
        url = f"{self.__base_uri}/api/v2/media"
        try:
            files = {"file": open(filename, "rb")}
            response = requests.post(url, headers=self.__headers, files=files)
            if response.status_code == 202:
                return response.json()
            message = f"HTTP Code: {response.status_code}. {response.text}"
            raise Exception(message)
        except Exception as exception:
            print(exception)
        return None

    def get_media_info(self, id):
        print("get_media_info")
        url = f"{self.__base_uri}/api/v1/media/{id}"
        print(url)
        try:
            response = requests.get(url, headers=self.__headers)
            if response.status_code == 200:
                return response.json()
            message = f"HTTP Code: {response.status_code}. {response.text}"
            raise Exception(message)
        except Exception as exception:
            print(exception)
        return None

    def toot_with_media(self, status, filename):
        response = self.upload_media(filename)
        if response and "blurhash" in response and response["blurhash"]:
            id = response['id']
            info = None
            tries = 0
            while info is None:
                info = self.get_media_info(id)
                sleep(30)
                tries += 1
                print(f"Try n {tries}")
                if tries > 10:
                    return None
            return self.toot(status, [id])


def main():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    base_uri = os.getenv("MASTODON_BASE_URI")
    access_token = os.getenv("MASTODON_ACCESS_TOKEN")
    mastodon_client = MastodonClient(base_uri, access_token)
    msg = "Nueva versión de Ubuntu"
    # mastodon_client.toot(msg, ["108255940858273411"])
    filename = "/home/lorenzo/kk/ubuntu.mp4"
    # salida = mastodon_client.upload_media(filename)
    # print(salida)
    # mastodon_client.toot_with_media(msg, filename)
    # print(mastodon_client.get_media_info("108255983701968389"))
    mastodon_client.toot_with_media(msg, filename)


if __name__ == "__main__":
    main()
