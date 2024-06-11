
import unittest
import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join("./src"))
from pprint import pprint
from ytdlman import YtDlMan


class TestTYDlMan(unittest.TestCase):
    def test_search(self):
        load_dotenv()
        yt_channel = os.getenv("YT_CHANNEL")
        videos = YtDlMan.get_videos(yt_channel, "2024-05-10T00:00:00Z")
        with open("prueba.json", "w") as fw:
            fw.write(videos)
        for video in videos:
            pprint(video)

        self.assertGreater(len(videos), 0)

