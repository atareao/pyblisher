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
from dotenv import load_dotenv
sys.path.append(os.path.join("./src"))
from linkedin import LinkedIn


class TestLinkedIn(unittest.TestCase):
    def test_post(self):
        load_dotenv()
        token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        org = os.getenv("LINKEDIN_ORGANIZATION")
        linkedin_client = LinkedIn(org, token)
        message = "Hola!"
        message = """
608 - Tu propia biblioteca digital con Kavita y Docker

Crea tu propia #biblioteca #digital de #libros #comics #manga en #linux utilizando #docker y #kavita para consumir tu contenido ...

https://www.youtube.com/watch?v=p3-JTLJhXNM

#atareaoConLinux #podcastesp
        """
        response = linkedin_client.send_message(message)
        self.assertIsNotNone(response)


if __name__ == '__main__':
    unittest.main()
