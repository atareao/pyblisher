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
import requests

logger = logging.getLogger(__name__)


class ZincClient:

    def __init__(self, base_url, indice, token):
        logger.debug("Zinc base url: %s", base_url)
        logger.debug("Zinc indice: %s", indice)
        self._url = f"https://{base_url}/api/{indice}/_doc"
        self._headers = {"Authorization": f"Basic {token}",
                         "Content-Type": "application/json",
                         "Accept": "application/json"}

    def populate(self, data):
        try:
            response = requests.post(self._url, headers=self._headers,
                                     json=data)
            logger.debug("Status code: %s", response.status_code)
            logger.debug("Response: %s", response.text)
            if response.status_code == 200:
                return response.json()
            raise Exception(f"Error: {response.status_code}. {response.text}")
        except Exception as exception:
            logger.error(exception)
