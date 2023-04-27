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

import unittest
import sys
import logging
import os
sys.path.append(os.path.join("../src"))
from table import Table

logger = logging.getLogger(__name__)


class Sample(Table):
    DATABASE = 'test.db'
    TABLE = 'SAMPLES'
    UNIKEYS = ['name']
    CREATE_TABLE_QUERY = f"""
    CREATE TABLE IF NOT EXISTS {TABLE}(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name STRING)
    """


class TestTable(unittest.TestCase):
    def setUp(self):
        if os.path.exists(Sample.DATABASE):
            os.remove(Sample.DATABASE)
        Sample.inicializate()

    def tearDown(self):
        if os.path.exists(Sample.DATABASE):
            os.remove(Sample.DATABASE)

    def test_exist_database(self):
        logger.info("=== Exists database ===")
        self.assertTrue(os.path.exists(Sample.DATABASE))

    def test_columns(self):
        logger.info("=== Test columns ===")
        columns = Sample.COLUMNS
        self.assertTrue('id' in columns)
        self.assertTrue('name' in columns)

    def test_create(self):
        logger.info("=== Test create item ===")
        sample1 = Sample.from_dict({"name": "Sample 1"})
        sample1.save()
        returned = Sample.get_by_id(sample1.id)
        self.assertIsNotNone(returned)
        self.assertEqual(sample1, returned)

    def test_differents(self):
        logger.info("=== Test differents ===")
        sample1 = Sample.from_dict({"name": "Sample 1"})
        sample1.save()
        logger.info(sample1.name)
        sample2 = Sample.from_dict({"name": "Sample 2"})
        sample2.save()
        logger.info(sample2.name)
        self.assertNotEqual(sample1, sample2)

    def test_exists(self):
        logger.info("=== Test exists ===")
        sample1 = Sample.from_dict({"name": "Sample 1"})
        sample1.save()
        sample2 = Sample.from_dict({"name": "Sample 1"})
        self.assertTrue(sample2.exists())

    def test_get_by_id(self):
        logger.info("=== Test get_by_id ===")
        sample1 = Sample.from_dict({"name": "Sample 1"})
        sample1.save()
        sample2 = Sample.get_by_id(sample1.id)
        self.assertEqual(sample1, sample2)

    def test_get_all(self):
        logger.info("=== Test get_all ===")
        sample1 = Sample.from_dict({"name": "Sample 1"})
        sample1.save()
        sample2 = Sample.from_dict({"name": "Sample 2"})
        sample2.save()
        sample3 = Sample.from_dict({"name": "Sample 3"})
        sample3.save()
        samples = Sample.get_all()
        self.assertEqual(len(samples), 3)

    def test_select(self):
        logger.info("=== Test select ===")
        sample1 = Sample.from_dict({"name": "Sample 1"})
        sample1.save()
        sample2 = Sample.from_dict({"name": "Sample 2"})
        sample2.save()
        sample3 = Sample.from_dict({"name": "Sample 3"})
        sample3.save()
        condition = "name='Sample 2'"
        samples = Sample.select(condition)
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].name, "Sample 2")


if __name__ == '__main__':
    unittest.main()
