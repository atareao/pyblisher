
import unittest
import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join("./src"))
from ytdlman import YtDlMan


class TestTYDlMan(unittest.TestCase):
    def test_search(self):
        load_dotenv()
        yt_channel = os.getenv("YT_CHANNEL")
        videos = YtDlMan.get_videos(yt_channel, "2024-06-10T00:00:00Z")
        self.assertGreater(len(videos), 0)

