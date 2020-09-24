import os

import requests


def _read_version(file):
    return open(os.path.join(os.path.dirname(__file__), file)).read().replace('\n', '')

class LaunchableClientFactory:
    BASE_URL_KEY = "LAUNCHABLE_REORDERING_BASE_URL"
    ORG_NAME_KEY = "LAUNCHABLE_REORDERING_ORG_NAME"
    WORKSPACE_NAME_KEY = "LAUNCHABLE_REORDERING_WORKSPACE_NAME"
    TARGET_NAME_KEY = "LAUNCHABLE_REORDERING_TARGET_NAME"
    API_TOKEN_KEY = "LAUNCHABLE_REORDERING_API_TOKEN"

    @classmethod
    def prepare(cls):
        return LaunchableClient(
            os.environ[cls.BASE_URL_KEY],
            os.environ[cls.ORG_NAME_KEY],
            os.environ[cls.WORKSPACE_NAME_KEY],
            os.environ[cls.TARGET_NAME_KEY],
            os.environ[cls.API_TOKEN_KEY],
            requests,
        )


class LaunchableClient:
    # TODO: Stop using a fictitious id once the server starts dynamic reordering
    FICTITIOUS_ID = "1"
    CLIENT_NAME = "nose-reorder"
    CLIENT_VERSION = _read_version('../version')

    def __init__(self, base_url, org_name, workspace_name, target_name, api_token, http):
        self.base_url = base_url
        self.org_name = org_name
        self.workspace_name = workspace_name
        self.target_name = target_name
        self.api_token = api_token
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
            'X-Client-Version': self.CLIENT_VERSION,
            'Authorization': 'Bearer {}'.format(self.api_token)
        }
        body = self._request_body(test)

        res = self.http.post(url, headers=headers, json=body)
        res.raise_for_status()

        return res.json()

    def _request_body(self, test):
        return {
            "targetName": self.target_name,
            "test": test,
            "session": {"id": self.FICTITIOUS_ID, "subject": self.FICTITIOUS_ID, "flavors": {}},
        }


