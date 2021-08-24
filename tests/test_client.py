import os
import subprocess
import unittest
from unittest.mock import MagicMock

from nose_launchable.case_event import CaseEvent
from nose_launchable.client import LaunchableClientFactory, LaunchableClient, TestSessionContext
from nose_launchable.version import __version__


class TestLaunchableClientFactory(unittest.TestCase):
    def setUp(self):
        os.environ[LaunchableClientFactory.TOKEN_KEY] = 'v1:org_name/wp_name:token'

    def test_prepare(self):
        client = LaunchableClientFactory.prepare()

        self.assertEqual('https://api.mercury.launchableinc.com', client.base_url)
        self.assertEqual('org_name', client.org_name)
        self.assertEqual('wp_name', client.workspace_name)
        self.assertEqual('v1:org_name/wp_name:token', client.token)
        self.assertIsNotNone(client.http)
        self.assertEqual(subprocess, client.process)

    def test_prepare_with_base_url(self):
        os.environ[LaunchableClientFactory.BASE_URL_KEY] = 'base_url'

        client = LaunchableClientFactory.prepare()

        self.assertEqual('base_url', client.base_url)
        self.assertEqual('org_name', client.org_name)
        self.assertEqual('wp_name', client.workspace_name)
        self.assertEqual('v1:org_name/wp_name:token', client.token)
        self.assertIsNotNone(client.http)
        self.assertEqual(subprocess, client.process)


class TestLaunchableClient(unittest.TestCase):
    def test_start(self):
        mock_response = MagicMock(name="response")
        mock_requests = MagicMock(name="requests")
        mock_response.json.return_value = {'id': 1}
        mock_requests.post.return_value = mock_response

        mock_subprocess = MagicMock(name="subprecess")

        client = LaunchableClient("base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess)
        client.start("test_build_number")

        expected_url = "base_url/intake/organizations/org_name/workspaces/wp_name/builds/test_build_number/test_sessions"
        expected_headers = {
            'Content-Type': 'application/json',
            'X-Client-Name': LaunchableClient.CLIENT_NAME,
            'X-Client-Version': __version__,
            'Authorization': 'Bearer token'
        }

        mock_requests.post.assert_called_once_with(
            expected_url, headers=expected_headers)
        mock_response.raise_for_status.assert_called_once_with()
        mock_response.json.assert_called_once_with()

        self.assertEqual("test_build_number",
                         client.build_number)
        self.assertEqual(
            "builds/test_build_number/test_sessions/1", client.test_session_context.get_build_path())

    def test_subset_success_with_target(self):
        mock_output = MagicMock(name="output")
        mock_subprocess = MagicMock(name="subprecess")

        mock_subprocess.run.return_value = mock_output
        mock_subprocess.PIPE = "PIPE"
        # Success
        mock_output.returncode = 0
        mock_output.stdout = "tests/test2.py\ntests/test1.py\n"

        mock_requests = MagicMock(name="requests")

        client = LaunchableClient(
            "base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess)
        client.test_session_context = TestSessionContext(
            build_number="test_subset_success_with_target", test_session_id=1)

        got = client.subset(["tests/test1.py", "tests/test2.py"], None, "10")

        expected_command = ['launchable', 'subset', '--session',
                            'builds/test_subset_success_with_target/test_sessions/1', '--target', '10%', 'file']
        expected_input = 'tests/test1.py\ntests/test2.py'

        mock_subprocess.run.assert_called_once_with(
            expected_command, input=expected_input, encoding='utf-8', stdout='PIPE', stderr='PIPE')
        self.assertEqual(['tests/test2.py', 'tests/test1.py'], got)

    def test_subset_success_with_options(self):
        mock_output = MagicMock(name="output")
        mock_subprocess = MagicMock(name="subprecess")

        mock_subprocess.run.return_value = mock_output
        mock_subprocess.PIPE = "PIPE"
        # Success
        mock_output.returncode = 0
        mock_output.stdout = "tests/test2.py\ntests/test1.py\n"

        mock_requests = MagicMock(name="requests")

        client = LaunchableClient(
            "base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess)
        client.test_session_context = TestSessionContext(
            build_number="test_subset_success_with_options", test_session_id=1)

        got = client.subset(
            ["tests/test1.py", "tests/test2.py"], '--target 10%', None)

        expected_command = ['launchable', 'subset', '--session',
                            'builds/test_subset_success_with_options/test_sessions/1', '--target', '10%', 'file']
        expected_input = 'tests/test1.py\ntests/test2.py'

        mock_subprocess.run.assert_called_once_with(
            expected_command, input=expected_input, encoding='utf-8', stdout='PIPE', stderr='PIPE')
        self.assertEqual(['tests/test2.py', 'tests/test1.py'], got)

    def test_subset_failure(self):
        mock_output = MagicMock(name="output")
        mock_subprocess = MagicMock(name="subprecess")

        mock_subprocess.run.return_value = mock_output
        mock_subprocess.PIPE = "PIPE"
        # Fail
        mock_output.returncode = 1
        mock_output.error = "error"

        mock_requests = MagicMock(name="requests")

        client = LaunchableClient(
            "base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess)
        client.test_session_context = TestSessionContext(
            build_number="test", test_session_id=1)

        with self.assertRaises(RuntimeError):
            client.subset(["tests/test1.py", "tests/test2.py"], None, "10")

    def test_upload_events(self):
        mock_response = MagicMock(name="response")
        mock_requests = MagicMock(name="requests")
        mock_requests.post.return_value = mock_response

        mock_subprocess = MagicMock(name="subprecess")

        client = LaunchableClient("base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess)

        mock_component1 = MagicMock(name="test_path_component1")
        mock_component1.to_body.return_value = {"type": "file", "name": "test1.py"}

        mock_component2 = MagicMock(name="test_path_component2")
        mock_component2.to_body.return_value = {"type": "file", "name": "test2.py"}

        events = [
            CaseEvent([mock_component1], 0.1, CaseEvent.TEST_PASSED, "stdout1", "stderr1"),
            CaseEvent([mock_component2], 0.2, CaseEvent.TEST_FAILED, "stdout2", "stderr2")
        ]

        client.build_number = 1
        client.test_session_context = TestSessionContext(
            build_number=1, test_session_id=2)

        client.upload_events(events)

        expected_url = "base_url/intake/organizations/org_name/workspaces/wp_name/builds/1/test_sessions/2/events"
        expected_headers = {
            'Content-Type': 'application/json',
            'X-Client-Name': LaunchableClient.CLIENT_NAME,
            'X-Client-Version': __version__,
            'Authorization': 'Bearer token'
        }

        expected_body = {
            "events": [
                {
                    "type": "case",
                    "testPath": [{"type": "file", "name": "test1.py"}],
                    "duration": 0.1,
                    "status": CaseEvent.TEST_PASSED,
                    "stdout": "stdout1",
                    "stderr": "stderr1",
                    "data": {'testPath': [{"type": "file", "name": "test1.py"}]},
                    "created_at": events[0].created_at
                },
                {
                    "type": "case",
                    "testPath": [{"type": "file", "name": "test2.py"}],
                    "duration": 0.2,
                    "status": CaseEvent.TEST_FAILED,
                    "stdout": "stdout2",
                    "stderr": "stderr2",
                    "data": {'testPath': [{"type": "file", "name": "test2.py"}]},
                    "created_at": events[1].created_at,
                }
            ]
        }

        mock_requests.post.assert_called_once_with(expected_url, headers=expected_headers, json=expected_body)
        mock_response.raise_for_status.assert_called_once_with()

    def test_finish(self):
        mock_response = MagicMock(name="response")
        mock_requests = MagicMock(name="requests")
        mock_requests.patch.return_value = mock_response

        client = LaunchableClient("base_url", "org_name", "wp_name",
                                  "token", mock_requests, MagicMock(name="subprecess"))
        client.test_session_context = TestSessionContext(
            build_number="test_build_number", test_session_id=1)

        client.finish()

        expected_url = "base_url/intake/organizations/org_name/workspaces/wp_name/builds/test_build_number/test_sessions/1/close"
        expected_headers = {
            'Content-Type': 'application/json',
            'X-Client-Name': LaunchableClient.CLIENT_NAME,
            'X-Client-Version': __version__,
            'Authorization': 'Bearer token'
        }

        mock_requests.patch.assert_called_once_with(expected_url, headers=expected_headers)
        mock_response.raise_for_status.assert_called_once_with()


class TestTSessionContext(unittest.TestCase):
    def test_get_build_path(self):
        context = TestSessionContext(build_number="1", test_session_id="2")
        self.assertEqual(context.get_build_path(),
                         "builds/1/test_sessions/2")

        context = TestSessionContext(build_number="aaa", test_session_id="bbb")
        self.assertEqual(context.get_build_path(),
                         "builds/aaa/test_sessions/bbb")
