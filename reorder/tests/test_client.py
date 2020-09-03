import os
import unittest
from unittest.mock import MagicMock

import requests
from reorder.client import LaunchableClientFactory, LaunchableClient, S3ClientFactory, S3Client


class TestLaunchableClientFactory(unittest.TestCase):
    def setUp(self):
        os.environ[LaunchableClientFactory.BASE_URL_KEY] = 'base_url'
        os.environ[LaunchableClientFactory.ORG_NAME_KEY] = 'org_name'
        os.environ[LaunchableClientFactory.WORKSPACE_NAME_KEY] = 'wp_name'
        os.environ[LaunchableClientFactory.API_TOKEN_KEY] = 'api_token'

    def test_prepare(self):
        client = LaunchableClientFactory.prepare()

        self.assertEqual('base_url', client.base_url)
        self.assertEqual('org_name', client.org_name)
        self.assertEqual('wp_name', client.workspace_name)
        self.assertEqual('api_token', client.api_token)
        self.assertEqual(requests, client.http)


class TestLaunchableClient(unittest.TestCase):
    def setUp(self):
        self.template = {
            "tests": [
                {
                    "className": "class0",
                    "name": "test0",
                    "buildNumber": 0,
                    "duration": 0,
                    "stdout": "class0 test0 stdout",
                    "stderr": "class0 test0 stderr",
                    "status": "PASSED",
                    "flavors": {}
                },
                {
                    "className": "class0",
                    "name": "test1",
                    "buildNumber": 1,
                    "duration": 1,
                    "stdout": "class0 test1 stdout",
                    "stderr": "class0 test1 stderr",
                    "status": "FAILED",
                    "flavors": {}
                },
            ]
        }

    def test_infer(self):
        mock_response = MagicMock(name="response")
        mock_requests = MagicMock(name="requests")
        mock_requests.post.return_value = mock_response

        client = LaunchableClient("base_url", "org_name", "wp_name", "api_token", mock_requests)

        names = [{"className": "class0", "name": "test0"}, {"className": "class0", "name": "test1"}]

        client.infer(names, self.template)

        expected_url = "base_url/intake/organizations/org_name/workspaces/wp_name/inference"
        expected_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer api_token'
        }
        expected_body = {
            "tests": [
                {
                    'buildNumber': 0,
                    'className': 'class0',
                    'name': 'test0',
                    'duration': 0,
                    'stdout': 'class0 test0 stdout',
                    'stderr': 'class0 test0 stderr',
                    'status': 'PASSED',
                    'flavors': {}
                },
                {
                    'buildNumber': 1,
                    'className': 'class0',
                    'name': 'test1',
                    'duration': 1,
                    'stdout': 'class0 test1 stdout',
                    'stderr': 'class0 test1 stderr',
                    'status': 'FAILED',
                    'flavors': {}
                }
            ]
        }

        mock_requests.post.assert_called_once_with(expected_url, headers=expected_headers, json=expected_body)
        mock_response.raise_for_status.assert_called_once_with()
        mock_response.json.assert_called_once_with()

    def test_infer_with_unknown_tests(self):
        mock_response = MagicMock(name="response")
        mock_requests = MagicMock(name="requests")
        mock_requests.post.return_value = mock_response

        client = LaunchableClient("base_url", "org_name", "wp_name", "api_token", mock_requests)

        names = [{"className": "class0", "name": "test0"}, {"className": "class1", "name": "test0"}]
        client.infer(names, self.template)

        expected_url = "base_url/intake/organizations/org_name/workspaces/wp_name/inference"
        expected_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer api_token'
        }
        expected_body = {
            "tests": [
                {
                    'buildNumber': 0,
                    'className': 'class0',
                    'name': 'test0',
                    'duration': 0,
                    'stdout': 'class0 test0 stdout',
                    'stderr': 'class0 test0 stderr',
                    'status': 'PASSED',
                    'flavors': {}
                },
                {
                    'buildNumber': 100,
                    'className': 'class1',
                    'name': 'test0',
                    'duration': 5,
                    'stdout': '',
                    'stderr': '',
                    'status': 'PASSED',
                    'flavors': {}
                }
            ]
        }

        mock_requests.post.assert_called_once_with(expected_url, headers=expected_headers, json=expected_body)
        mock_response.raise_for_status.assert_called_once_with()
        mock_response.json.assert_called_once_with()


class TestLS3ClientFactory(unittest.TestCase):
    def setUp(self):
        os.environ[S3ClientFactory.AWS_ACCESS_KEY_ID_KEY] = 'access_key_id'
        os.environ[S3ClientFactory.AWS_SECRET_ACCESS_KEY_KEY] = 'secret_key'

    def test_prepare(self):
        client = S3ClientFactory.prepare()
        self.assertTrue(isinstance(client, S3Client))
