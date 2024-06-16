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

import unittest
import sys
import os
sys.path.append(os.path.join("./src"))
from table import Table
from video import Video
from utils import process

Table.DATABASE = 'test.db'


class TestVideo(unittest.TestCase):
    def setUp(self):
        if os.path.exists(Table.DATABASE):
            os.remove(Table.DATABASE)
        Video.inicializate()

    def tearDown(self):
        if os.path.exists(Table.DATABASE):
            os.remove(Table.DATABASE)

    def test_create(self):
        avideo = Video.new("titulo", "description", "yt_id", "link", "fecha")
        tvideo = Video.get_by_id(avideo.id)
        self.assertEqual(avideo, tvideo)
    
    def test_process(self):
        avideo = Video.new("titulo", "description", "yt_id", "link", "fecha")
        tvideo = Video.get_by_id(avideo.id)
        template = "twitter.html"
        processed = process(tvideo, template)
        print(processed)
        self.assertIsNotNone(processed)


if __name__ == '__main__':
    unittest.main()
