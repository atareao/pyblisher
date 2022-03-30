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

from table import Table

class Schedule(Table):
    TABLE = 'SCHEDULE'
    PK = 'ID'
    UNIKEYS = ['DAY']
    CREATE_TABLE_QUERY = (f"CREATE TABLE IF NOT EXISTS {TABLE}("
                          f"{PK} INTEGER PRIMARY KEY AUTOINCREMENT,"
                          "DAY TEXT,"
                          "LIST_ID INTEGER,"
                          "PUBLISH BOOLEAN DEFAULT FALSE)")

    @classmethod
    def print(cls):
        sql = ("SELECT s.id, s.day, l.title, s.publish FROM schedule s "
               "LEFT JOIN listas l on s.list_id=l.id ORDER BY s.id")
        data = cls.raw_query(sql)
        print(data)
