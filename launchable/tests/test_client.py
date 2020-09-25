import os
import unittest
from unittest.mock import MagicMock

import requests
from launchable.client import LaunchableClientFactory, LaunchableClient
from launchable.version import __version__


class TestLaunchableClientFactory(unittest.TestCase):
    def setUp(self):
        os.environ[LaunchableClientFactory.API_TOKEN_KEY] = 'v1:org_name/wp_name:token'

    def test_prepare(self):
        client = LaunchableClientFactory.prepare()

        self.assertEqual('https://api.mercury.launchableinc.com', client.base_url)
        self.assertEqual('org_name', client.org_name)
        self.assertEqual('wp_name', client.workspace_name)
        self.assertEqual('token', client.token)
        self.assertEqual(requests, client.http)

    def test_prepare_with_base_url(self):
        os.environ[LaunchableClientFactory.BASE_URL_KEY] = 'base_url'

        client = LaunchableClientFactory.prepare()

        self.assertEqual('base_url', client.base_url)
        self.assertEqual('org_name', client.org_name)
        self.assertEqual('wp_name', client.workspace_name)
        self.assertEqual('token', client.token)
        self.assertEqual(requests, client.http)


class TestLaunchableClient(unittest.TestCase):

    def test_infer(self):
        mock_response = MagicMock(name="response")
        mock_requests = MagicMock(name="requests")
        mock_requests.post.return_value = mock_response

        client = LaunchableClient("base_url", "org_name", "wp_name", "token", mock_requests)

        test = {
            "type": "tree",
            "root": {
                "type": "testCaseNode",
                "testName": "class0.test0"
            }
        }

        client.infer(test)

        expected_url = "base_url/intake/organizations/org_name/workspaces/wp_name/inference"
        expected_headers = {
            'Content-Type': 'application/json',
            'X-Client-Name': LaunchableClient.CLIENT_NAME,
            'X-Client-Version': __version__,
            'Authorization': 'Bearer token'
        }

        expected_body = {
            'test': {'type': 'tree', 'root': {'type': 'testCaseNode', 'testName': 'class0.test0'}},
            "session": {'id': '1', 'subject': '1', 'flavors': {}},
        }

        mock_requests.post.assert_called_once_with(expected_url, headers=expected_headers, json=expected_body)
        mock_response.raise_for_status.assert_called_once_with()
        mock_response.json.assert_called_once_with()
