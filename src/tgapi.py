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

import requests
import logging

logger = logging.getLogger(__name__)


def main():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    message = "Nueva versión de Ubuntu"
    group = os.getenv("TELEGRAM_GROUP")
    token = os.getenv("TELEGRAM_TOKEN")
    if group is not None and group.find(","):
        group_id, theme_id = group.split(",")
        data = {"chat_id": group_id, 
                "text": message,
                "message_thread_id": theme_id}
    else:
        data = {"chat_id": group, 
                "text": message}
    print(data)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    print(url)
    response = requests.post(url, data=data)
    print(response)
    print(response.text)


if __name__ == "__main__":
    main()

