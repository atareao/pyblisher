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
sys.path.append(os.path.join("../src"))
from table import Table
from lista import Lista
from schedule import Schedule

Table.DATABASE = 'test.db'

class TestSchedule(unittest.TestCase):
    def setUp(self):
        if os.path.exists(Table.DATABASE):
            os.remove(Table.DATABASE)
        Lista.inicializate()
        Schedule.inicializate()

    def tearDown(self):
        if os.path.exists(Table.DATABASE):
            os.remove(Table.DATABASE)

    def test_create(self):
        schedule = Schedule.from_dict({
            "day": "Lunes",
            "publish": True
            })
        schedule.save()
        schedule.print()
        alista = Lista.from_dict({"yt_id": "1", "title": "titulo1",
            "reverse": True})
        alista.save()
        schedule.list_id = alista.id
        schedule.save()
        schedule.print()


if __name__ == '__main__':
    unittest.main()
