import logging
import requests
import uuid


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

    def init_client(self, client_id: str, client_secret: str):
        self._client_id = client_id
        self._client_secret = client_secret

    def get_auth_code(self):
        url = "https://www.linkedin.com/oauth/v2/authorization"
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": "https://pub.territoriolinux.es/linkedin/redirect",
            "state": uuid.uuid4().hex,
            "scope": "openid email profile w_member_social"
        }
        response = requests.get(url, params=params, timeout=TIMEOUT)
        if not response.ok:
            raise LinkedInException(f"Error: {response.text}")
        return response.text

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
        print("payload: %s", payload)
        url = f"{self._base_url}/v2/ugcPosts"
        response = requests.post(url, json=payload, headers=self._headers,
                                 timeout=TIMEOUT)
        if not response.ok:
            raise LinkedInException(f"Error: {response.text}")
        return response

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    organization = os.getenv("LINKEDIN_ORGANIZATION", "")
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    print(organization, access_token)
    client = LinkedIn(organization, access_token)
    client.send_message("test")
