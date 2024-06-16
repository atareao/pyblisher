import logging
import requests


logger = logging.getLogger(__name__)
TIMEOUT = (5, 60)


class DiscordException(Exception):
    pass


class Discord:
    def __init__(self, channel: str, token: str):
        self._base_url = f"https://discord.com/api/webhooks/{channel}/{token}"

    def send_message(self, message: str):
        logger.info("send_message: %s", message)
        payload = {
            "content": message
        }
        response = requests.post(self._base_url, data=payload, timeout=TIMEOUT)
        if not response.ok:
            raise DiscordException(f"Error: {response.text}")
