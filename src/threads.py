import logging
import json
import requests


logger = logging.getLogger(__name__)
TIMEOUT = (5, 60)
BASE_URL = "https://graph.threads.net"


class ThreadsException(Exception):
    pass


class Threads:
    def __init__(self, config_file):
        self._config_file = config_file
        self._load()

    def _load(self):
        logger.debug("load config")
        with open(self._config_file, "r") as fr:
            self._config = json.load(fr)

    def _save(self):
        logger.debug("save config")
        with open(self._config_file, "w") as fw:
            json.dump(self._config, fw)

    def get_access_token(self):
        data = {
            "grant_type": "th_refresh_token",
            "access_token": self._config["access_token"]
        }
        url = f"{BASE_URL}/refresh_access_token"
        response = requests.post(url, data=data, timeout=TIMEOUT)
        if response.status_code != 200:
            raise ThreadsException(f"Error: {response.text}")
        self._config["access_token"] = response.json()["access_token"]
        self._save()

    def get_me(self):
        params = {
            "access_token": self._config["access_token"]
        }
        url = f"{BASE_URL}/v1.0/me"
        response = requests.get(url, params=params, timeout=TIMEOUT)
        if response.status_code != 200:
            raise ThreadsException(f"Error: {response.text}")
        return response.json()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    threads = Threads("config.json")
    threads.get_access_token()
    print(threads.get_me())

