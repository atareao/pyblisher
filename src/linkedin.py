import logging
import requests


logger = logging.getLogger(__name__)
TIMEOUT = (5, 60)


class LinkedInException(Exception):
    pass


class LinkedIn:
    def __init__(self, organization=None, token=None):
        self._base_url = "https://api.linkedin.com"
        self._organization = organization
        self._headers = {
            "Authorization": f"Bearer {token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

    def send_message(self, message: str):
        logger.info("send_message: %s", message)
        payload = {
            "author": f"urn:li:organization:{self._organization}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": message
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        url = f"{self._base_url}/v2/ugcPosts"
        response = requests.post(url, json=payload, headers=self._headers,
                                 timeout=TIMEOUT)
        if not response.ok:
            raise LinkedInException(f"Error: {response.text}")
        return response
