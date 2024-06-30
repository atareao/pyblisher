import logging
import requests
import retry


logger = logging.getLogger(__name__)
TIMEOUT = (5, 60)


class TelegramException(Exception):
    pass


class Telegram:
    def __init__(self, token=None):
        self._base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, message: str, chat_id, thread_id=None):
        logger.info("send_message: %s", message)
        payload = {
            "chat_id": chat_id,
            "message_thread_id": thread_id if thread_id else 0,
            "text": message
        }
        url = f"{self._base_url}/sendMessage"
        response = requests.post(url, data=payload, timeout=TIMEOUT)
        if not response.ok:
            raise TelegramException(f"Error: {response.text}")

    def send_video(self, message: str, filename: str, chat_id, thread_id=None):
        logger.info("send_video: %s", message)
        payload = {
            "chat_id": chat_id,
            "message_thread_id": thread_id if thread_id else 0,
            "caption": message
        }
        url = f"{self._base_url}/sendVideo"
        with open(filename, "rb") as fr:
            response = requests.post(url, data=payload, files={"video": fr},
                                     timeout=TIMEOUT)
            if not response.ok:
                raise TelegramException(f"Error: {response.text}")
