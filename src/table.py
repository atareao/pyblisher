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

import sqlite3
from utils import Log
from collections import OrderedDict


class NoUnikeys(Exception):
    def __init__(self):
        message = 'No unique keys defined'
        super().__init__(message)


class Table:
    DATABASE = '/app/database/database.db'
    TABLE = 'TABLE'
    CREATE_TABLE_QUERY = ''
    UNIKEYS = []
    COLUMNS = {}

    def __init__(self):
        for column in self.COLUMNS:
            setattr(self, column, None)

    @classmethod
    def inicializate(cls):
        cls.__execute(cls.CREATE_TABLE_QUERY)
        cls.COLUMNS = cls.__get_columns()

    @classmethod
    def __execute(cls, sqlquery, data=None):
        lastrowid = None
        conn = None
        try:
            conn = sqlite3.connect(cls.DATABASE)
            cursor = conn.cursor()
            Log.info(sqlquery)
            if data:
                lastrowid = cursor.execute(sqlquery, data).lastrowid
            else:
                lastrowid = cursor.execute(sqlquery).lastrowid
            conn.commit()
        except Exception as exception:
            Log.error(exception)
            lastrowid = None
        finally:
            if conn:
                conn.close()
        return lastrowid

    @classmethod
    def __select(cls, sqlquery):
        conn = None
        try:
            conn = sqlite3.connect(cls.DATABASE)
            cursor = conn.cursor()
            Log.info(sqlquery)
            cursor.execute(sqlquery)
            return cursor.fetchall()
        except Exception as exception:
            Log.error(exception)
        finally:
            if conn:
                conn.close()
        return []

    @classmethod
    def __get_columns(cls):
        columns = {}
        sqlquery = f"PRAGMA table_info({cls.TABLE});"
        data = cls.__select(sqlquery)
        for row in data:
            name = row[1].lower()
            columns[name] = {"data_type": row[2], "pk": (row[5] == 1)}
            if row[5] == 1:
                cls.PK = name
        return OrderedDict(columns)

    def set(self, column, value):
        if value:
            if self.COLUMNS[column]['data_type'] == 'INTEGER':
                value = int(value) if value else None
            elif self.COLUMNS[column]['data_type'] == 'TEXT':
                value = str(value) if value else None
            elif self.COLUMNS[column]['data_type'] == 'BOOLEAN':
                value = bool(value) if value else None
        setattr(self, column, value)

    def get(self, column):
        value = getattr(self, column)
        if value:
            if self.COLUMNS[column]['data_type'] == 'INTEGER':
                return int(value)
            elif self.COLUMNS[column]['data_type'] == 'TEXT':
                return str(value)
            elif self.COLUMNS[column]['data_type'] == 'BOOLEAN':
                return bool(value)
        return value

    @classmethod
    def from_dict(cls, adict):
        item = cls()
        for column in cls.COLUMNS:
            if column in adict.keys() and cls.COLUMNS[column]['pk'] is False:
                setattr(item, column, adict[column])
        return item

    @classmethod
    def from_list(cls, result):
        item = cls()
        for index, column in enumerate(cls.COLUMNS):
            setattr(item, column, result[index])
        return item

    def save(self):
        keys = list(self.COLUMNS.keys())
        pk = self.get_pk()
        if self.get(pk):
            keys.remove(pk)
            set_values = ",".join([f"{key}=?" for key in keys])
            sqlquery = f"UPDATE {self.TABLE} SET {set_values} "\
                       f"WHERE {pk}=?"
            data = [self.get(key) for key in keys]
            data.append(self.get(pk))
            self.__execute(sqlquery, data)
        else:
            set_values = ",".join(keys)
            set_data = ("?,"*len(keys))[:-1]
            sqlquery = "INSERT INTO {} ({}) VALUES ({})".format(
                    self.TABLE, set_values, set_data)
            data = [self.get(key) for key in keys]
            self.set(pk, self.__execute(sqlquery, data))

    def exists(self):
        if self.UNIKEYS:
            condition = []
            for key in self.UNIKEYS:
                value = self.get(key)
                condition.append(f"{key}='{value}'")
            strcondition = ' and '.join(condition)
            items = self.select(strcondition)
            return len(items) > 0
        raise NoUnikeys

    @classmethod
    def get_by_id(cls, id):
        pk = cls.get_pk()
        condition = f"{pk}='{id}'"
        items = cls.select(condition)
        return items[0] if len(items) > 0 else None

    @classmethod
    def get_all(cls):
        return cls.select()

    @classmethod
    def get_pk(cls):
        for key, value in cls.COLUMNS.items():
            if value['pk'] is True:
                return key
        return None

    @classmethod
    def select(cls, condition=None):
        columns = ','.join(cls.COLUMNS)
        sqlquery = f"SELECT {columns} FROM {cls.TABLE}"
        if condition:
            if isinstance(condition, list):
                if len(condition) > 1:
                    condition = " AND ".join(condition)
                else:
                    condition = condition[0]
            sqlquery += f" WHERE {condition}"
        items = []
        result = cls.__select(sqlquery)
        if result:
            for item in result:
                items.append(cls.from_list(item))
        return items

    @classmethod
    def query(cls, sqlquery):
        return cls.select(sqlquery)

    @classmethod
    def raw_query(cls, sqlquery):
        return cls.__select(sqlquery)

    def serialize(self):
        result = {}
        for column in self.COLUMNS:
            result[column] = self.get(column)
        return result

    def __repr__(self):
        name = type(self).__name__
        pk = self.get_pk()
        id = self.get(pk)
        return f'<{name} {id}>'

    def __iter__(self):
        for column in self.COLUMNS:
            yield(column, self.get(column))

    def __str__(self):
        result = []
        for column in self.COLUMNS:
            value = self.get(column)
            result.append(f"{column}: {value}")
        return "\n".join(result)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.UNIKEYS:
            for key in self.UNIKEYS:
                if getattr(self, key.lower()) != getattr(other, key.lower()):
                    return False
            return True
        raise NoUnikeys
