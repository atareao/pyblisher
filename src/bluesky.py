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

import re
import requests
import sys
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class BlueSkyClient:
    def __init__(self, base_url, user, password):
        self._base_url = base_url
        self._session = self._get_login_session(user, password)

    def _get_login_session(self, user, password):
        logger.debug("self._get_login_session")
        url = f"{self._base_url}/xrpc/com.atproto.server.createSession"
        logger.debug(f"Url: {url}")
        data = {
                "identifier": user,
                "password": password
            }
        logger.debug(f"data: {data}")
        resp = requests.post(url, json=data)
        resp.raise_for_status()
        return resp.json()

    def _post(self, message):
        # trailing "Z" is preferred over "+00:00"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # these are the required fields which every post must include
        post = {
            "$type": "app.bsky.feed.post",
            "text": message,
            "createdAt": now,
            "langs": ["es-ES"],
        }
        facets = self.parse_facets(message)
        if facets:
            post["facets"] = facets

        url = f"{self._base_url}/xrpc/com.atproto.repo.createRecord"
        headers = {"Authorization": "Bearer " + self._session["accessJwt"]}
        data = {
            "repo": self._session["did"],
            "collection": "app.bsky.feed.post",
            "record": post
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        message_error = f"Error {response.status_code}: {response.text}"
        raise Exception(message_error)

    def post(self, message):
        try:
            response = self._post(message)
            logger.debug(response)
        except Exception as exception:
            logger.error(exception)

    def parse_facets(self, text):
        """
        parses post text and returns a list of app.bsky.richtext.facet objects
        for any mentions (@handle.example.com) or URLs (https://example.com)

        indexing must work with UTF-8 encoded bytestring offsets, not regular
        unicode string offsets, to match Bluesky API expectations
        """
        facets = []
        url = f"{self._base_url}/xrpc/com.atproto.identity.resolveHandle"
        for m in self.parse_mentions(text):
            resp = requests.get(url, params={"handle": m["handle"]})
            # if handle couldn't be resolved, just skip it! will be text in the
            # post
            if resp.status_code == 400:
                continue
            did = resp.json()["did"]
            facets.append(
                {
                    "index": {
                        "byteStart": m["start"],
                        "byteEnd": m["end"],
                    },
                    "features": [{"$type": "app.bsky.richtext.facet#mention",
                                  "did": did}],
                }
            )
        for u in self.parse_urls(text):
            facets.append(
                {
                    "index": {
                        "byteStart": u["start"],
                        "byteEnd": u["end"],
                    },
                    "features": [
                        {
                            "$type": "app.bsky.richtext.facet#link",
                            # NOTE: URI ("I") not URL ("L")
                            "uri": u["url"],
                        }
                    ],
                }
            )
        return facets

    @staticmethod
    def parse_mentions(text):
        spans = []
        # regex based on: https://atproto.com/specs/handle#handle-identifier-syntax
        mention_regex = rb"[$|\W](@([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)"
        text_bytes = text.encode("UTF-8")
        for m in re.finditer(mention_regex, text_bytes):
            spans.append(
                {
                    "start": m.start(1),
                    "end": m.end(1),
                    "handle": m.group(1)[1:].decode("UTF-8"),
                }
            )
        return spans

    @staticmethod
    def parse_urls(text):
        spans = []
        # partial/naive URL regex based on: https://stackoverflow.com/a/3809435
        # tweaked to disallow some training punctuation
        url_regex = rb"[$|\W](https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*[-a-zA-Z0-9@%_\+~#//=])?)"
        text_bytes = text.encode("UTF-8")
        for m in re.finditer(url_regex, text_bytes):
            spans.append(
                {
                    "start": m.start(1),
                    "end": m.end(1),
                    "url": m.group(1).decode("UTF-8"),
                }
            )
        return spans
