import os

import requests

from launchable.log import logger
from launchable.version import __version__


class LaunchableClientFactory:
    BASE_URL_KEY = "LAUNCHABLE_BASE_URL"
    TOKEN_KEY = "LAUNCHABLE_TOKEN"

    DEFAULT_BASE_URL = "https://api.mercury.launchableinc.com"

    @classmethod
    def prepare(cls):
        url, org, wp, token = cls._parse_options()

        return LaunchableClient(url, org, wp, token, requests)

    @classmethod
    def _parse_options(cls):
        token = os.environ[cls.TOKEN_KEY]

        _, user, _ = token.split(":", 2)
        org, workplace = user.split("/", 1)

        return cls._get_base_url(), org, workplace, token

    @classmethod
    def _get_base_url(cls):
        return os.getenv(cls.BASE_URL_KEY) or cls.DEFAULT_BASE_URL


class LaunchableClient:
    # TODO: Stop using a fictitious id once the server starts dynamic reordering
    FICTITIOUS_ID = "1"
    CLIENT_NAME = "nose-launchable"

    def __init__(self, base_url, org_name, workspace_name, token, http):
        self.base_url = base_url
        self.org_name = org_name
        self.workspace_name = workspace_name
        self.token = token
        self.http = http

    def infer(self, test):
        url = "{}/intake/organizations/{}/workspaces/{}/inference".format(
            self.base_url,
            self.org_name,
            self.workspace_name
        )

        headers = {
            'Content-Type': 'application/json',
            'X-Client-Name': self.CLIENT_NAME,
            'X-Client-Version': __version__,
            'Authorization': 'Bearer {}'.format(self.token)
        }
        request_body = self._request_body(test)

        logger.debug("Request body: {}".format(request_body))

        res = self.http.post(url, headers=headers, json=request_body)
        logger.debug("Response status code: {}".format(res.status_code))
        res.raise_for_status()

        response_body = res.json()
        logger.debug("Response body: {}".format(response_body))

        return response_body

    def _request_body(self, test):
        return {
            "test": test,
            "session": {"id": self.FICTITIOUS_ID, "subject": self.FICTITIOUS_ID, "flavors": {}},
        }


