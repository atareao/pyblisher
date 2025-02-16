import json
import logging
import requests


logger = logging.getLogger(__name__)
TIMEOUT = (5, 60)
BASE_URL = "https://graph.threads.net"


class ThreadsException(Exception):
    pass


class Threads:
    def __init__(self, config_file):
        self._config_file = config_file
        self._config = {}
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
        logger.debug("get access token")
        params = {
            "grant_type": "th_refresh_token",
            "access_token": self._config["access_token"]
        }
        url = f"{BASE_URL}/refresh_access_token"
        response = requests.get(url, params=params, timeout=TIMEOUT)
        if response.status_code != 200:
            raise ThreadsException(f"Error: {response.text}")
        self._config["access_token"] = response.json()["access_token"]
        self._save()

    def get_me(self):
        logger.debug("get me")
        params = {
            "access_token": self._config["access_token"],
            "fields": ("id,username,name,threads_profile_picture_url,"
                       "threads_biography")
        }
        url = f"{BASE_URL}/v1.0/{self._config['user_id']}"
        response = requests.get(url, params=params, timeout=TIMEOUT)
        if response.status_code != 200:
            raise ThreadsException(f"Error: {response.text}")
        return response.json()

    def _publish(self, id):
        logger.debug("publish")
        data = {
            "creation_id": id,
            "access_token": self._config["access_token"]
        }
        url = f"{BASE_URL}/v1.0/{self._config['user_id']}/threads_publish"
        response = requests.post(url, data=data, timeout=TIMEOUT)
        if response.status_code != 200:
            raise ThreadsException(f"Error: {response.text}")
        return response.json()

    def populate_text(self, text):
        logger.debug("populate message")
        data = {
            "domain": self._config["domain"],
            "text": text,
            "media_type": "TEXT",
            "access_token": self._config["access_token"]
        }
        url = f"{BASE_URL}/v1.0/{self._config['user_id']}/threads"
        response = requests.post(url, data=data, timeout=TIMEOUT)
        if response.status_code != 200:
            raise ThreadsException(f"Error: {response.text}")
        id = response.json()["id"]
        return self._publish(id)

    def populate_image(self, text, image_url):
        logger.debug("populate message")
        data = {
            "domain": self._config["domain"],
            "text": text,
            "image_url": image_url,
            "media_type": "IMAGE",
            "access_token": self._config["access_token"]
        }
        url = f"{BASE_URL}/v1.0/{self._config['user_id']}/threads"
        response = requests.post(url, data=data, timeout=TIMEOUT)
        if response.status_code != 200:
            raise ThreadsException(f"Error: {response.text}")
        id = response.json()["id"]
        return self._publish(id)

    def populate_video(self, text, video_url):
        logger.debug("populate message")
        data = {
            "domain": self._config["domain"],
            "text": text,
            "video_url": video_url,
            "media_type": "VIDEO",
            "access_token": self._config["access_token"]
        }
        url = f"{BASE_URL}/v1.0/{self._config['user_id']}/threads"
        response = requests.post(url, data=data, timeout=TIMEOUT)
        if response.status_code != 200:
            raise ThreadsException(f"Error: {response.text}")
        logger.debug(response.text)
        id = response.json()["id"]
        logger.debug(f"Id: {id}")
        return self._publish(id)

    def get_media_status(self, id):
        logger.debug("media status")
        params = {
            "fields": "status,error_message",
            "access_token": self._config["access_token"]
        }
        url = f"{BASE_URL}/v1.0/{id}"
        response = requests.get(url, params=params, timeout=TIMEOUT)
        if response.status_code != 200:
            raise ThreadsException(f"Error: {response.text}")
        return response.json()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    threads = Threads("threads.conf")
    threads.get_access_token()
    print(threads.get_me())
    message = "En este primer vídeo te muestro como puedes instalar NeoVim en Ubuntu, y prácticamente en cualquier otra distribución, porque lo realizo con AppImage. Por otro lado, establecemos la estructura básica para la configuración y los primeros elementos de la misma. Tanto la configuración básica como los atajos de teclado. https://www.youtube.com/watch?v=SoDjVPr5_Go"
    print(threads.populate_text(message))


