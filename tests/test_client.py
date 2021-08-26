import os
import subprocess
import unittest
from unittest import mock
from unittest.mock import MagicMock, call

from nose_launchable.case_event import CaseEvent
from nose_launchable.client import LaunchableClientFactory, LaunchableClient, TestSessionContext
from nose_launchable.version import __version__


class TestLaunchableClientFactory(unittest.TestCase):

    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": 'v1:org_name/wp_name:token', })
    def test_prepare_with_build_number(self):
        client = LaunchableClientFactory.prepare("test", None)

        self.assertEqual(
            'https://api.mercury.launchableinc.com', client.base_url)
        self.assertEqual('org_name', client.org_name)
        self.assertEqual('wp_name', client.workspace_name)
        self.assertEqual('v1:org_name/wp_name:token', client.token)
        self.assertIsNotNone(client.http)
        self.assertEqual(subprocess, client.process)
        self.assertEqual("test", client.test_session_context.build_number)
        self.assertIsNone(client.test_session_context.test_session_id)
        self.assertTrue(client.test_session_context.registered_test_session())

    @mock.patch.dict(os.environ, {"LAUNCHABLE_TOKEN": 'v1:org_name/wp_name:token', })
    def test_prepare_with_test_session(self):
        client = LaunchableClientFactory.prepare(None, "builds/test/test_sessions/1")

        self.assertEqual(
            'https://api.mercury.launchableinc.com', client.base_url)
        self.assertEqual('org_name', client.org_name)
        self.assertEqual('wp_name', client.workspace_name)
        self.assertEqual('v1:org_name/wp_name:token', client.token)
        self.assertIsNotNone(client.http)
        self.assertEqual(subprocess, client.process)
        self.assertEqual("test", client.test_session_context.build_number)
        self.assertEqual("1", client.test_session_context.test_session_id)
        self.assertFalse(client.test_session_context.registered_test_session())

    @mock.patch.dict(os.environ, {
        "LAUNCHABLE_TOKEN": 'v1:org_name/wp_name:token',
        "LAUNCHABLE_BASE_URL": 'base_url'
    })
    def test_prepare_with_base_url(self):
        client = LaunchableClientFactory.prepare("test", None)

        self.assertEqual('base_url', client.base_url)
        self.assertEqual('org_name', client.org_name)
        self.assertEqual('wp_name', client.workspace_name)
        self.assertEqual('v1:org_name/wp_name:token', client.token)
        self.assertIsNotNone(client.http)
        self.assertEqual(subprocess, client.process)


class TestLaunchableClient(unittest.TestCase):
    def test_start_without_test_session(self):
        mock_response = MagicMock(name="response")
        mock_requests = MagicMock(name="requests")
        mock_response.json.return_value = {'id': 1}
        mock_requests.post.return_value = mock_response
        mock_subprocess = MagicMock(name="subprecess")
        mock_context = TestSessionContext("test_build_number")

        client = LaunchableClient(
            "base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess, mock_context)
        client.start()

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

    def test_start_with_test_session(self):
        mock_response = MagicMock(name="response")
        mock_requests = MagicMock(name="requests")
        mock_subprocess = MagicMock(name="subprecess")

        mock_context = TestSessionContext("test_build_number", "1")

        client = LaunchableClient(
            "base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess, mock_context)
        client.start()

        mock_response.assert_not_called()
        mock_requests.assert_not_called()
        mock_subprocess.assert_not_called()

    def test_subset_success_with_target(self):
        mock_output = MagicMock(name="output")
        mock_subprocess = MagicMock(name="subprecess")

        mock_subprocess.run.return_value = mock_output
        mock_subprocess.PIPE = "PIPE"

        mock_context = TestSessionContext("test", 1)
        # Success
        mock_output.returncode = 0
        mock_output.stdout = "tests/test2.py\ntests/test1.py\n"

        mock_requests = MagicMock(name="requests")

        client = LaunchableClient(
            "base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess, mock_context)

        got = client.subset(["tests/test1.py", "tests/test2.py"], None, "10")

        expected_command = ['launchable', 'subset', '--session',
                            'builds/test/test_sessions/1', '--target', '10%', 'file']
        expected_input = 'tests/test1.py\ntests/test2.py'

        mock_subprocess.run.assert_called_once_with(
            expected_command, input=expected_input, encoding='utf-8', stdout='PIPE', stderr='PIPE')
        self.assertEqual(['tests/test2.py', 'tests/test1.py'], got)

    def test_subset_success_with_options(self):
        mock_output = MagicMock(name="output")
        mock_subprocess = MagicMock(name="subprecess")

        mock_subprocess.run.return_value = mock_output
        mock_subprocess.PIPE = "PIPE"

        mock_context = TestSessionContext("test", 1)
        # Success
        mock_output.returncode = 0
        mock_output.stdout = "tests/test2.py\ntests/test1.py\n"

        mock_requests = MagicMock(name="requests")

        client = LaunchableClient(
            "base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess, mock_context)

        got = client.subset(
            ["tests/test1.py", "tests/test2.py"], '--target 10%', None)

        expected_command = ['launchable', 'subset', '--session',
                            'builds/test/test_sessions/1', '--target', '10%', 'file']

        expected_input = 'tests/test1.py\ntests/test2.py'

        mock_subprocess.run.assert_called_once_with(
            expected_command, input=expected_input, encoding='utf-8', stdout='PIPE', stderr='PIPE')
        self.assertEqual(['tests/test2.py', 'tests/test1.py'], got)

    def test_split_subset(self):
        mock_subset = MagicMock(name="subset")
        mock_subset.stdout = "/subset/123"
        mock_subset.returncode = 0

        mock_split_subset = MagicMock(name="split-subset")
        mock_split_subset.stdout = "tests/test2.py"
        mock_split_subset.returncode = 0

        mock_output = MagicMock(name="output")
        mock_subprocess = MagicMock(name="subprecess")
        mock_subprocess.run = mock_output
        mock_output.side_effect = [
            mock_subset,
            mock_split_subset,
        ]
        mock_subprocess.PIPE = "PIPE"

        mock_context = TestSessionContext("test", 1)

        mock_requests = MagicMock(name="requests")

        client = LaunchableClient(
            "base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess, mock_context)

        got = client.subset(
            ["tests/test1.py", "tests/test2.py"], '--target 30% --bin 1/2', None)

        expected_subset_command = ['launchable', 'subset', '--session',
                                   'builds/test/test_sessions/1', '--target', '30%', '--split', 'file']

        expected_split_subset_command = [
            'launchable', 'split-subset', '--subset-id', "/subset/123", '--bin', "1/2", 'file']
        expected_input = 'tests/test1.py\ntests/test2.py'

        mock_subprocess.run.assert_has_calls(
            [
                call(expected_subset_command, input=expected_input,
                     encoding='utf-8', stdout='PIPE', stderr='PIPE'),
                call(expected_split_subset_command,
                     encoding='utf-8', stdout='PIPE', stderr='PIPE'),
            ])
        self.assertEqual(['tests/test2.py'], got)

    def test_subset_failure(self):
        mock_output = MagicMock(name="output")
        mock_subprocess = MagicMock(name="subprecess")

        mock_subprocess.run.return_value = mock_output
        mock_subprocess.PIPE = "PIPE"

        mock_context = TestSessionContext("test", 1)
        # Fail
        mock_output.returncode = 1
        mock_output.error = "error"

        mock_requests = MagicMock(name="requests")

        client = LaunchableClient(
            "base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess, mock_context)

        with self.assertRaises(RuntimeError):
            client.subset(["tests/test1.py", "tests/test2.py"], None, "10")

    def test_upload_events(self):
        mock_response = MagicMock(name="response")
        mock_requests = MagicMock(name="requests")
        mock_requests.post.return_value = mock_response

        mock_subprocess = MagicMock(name="subprecess")

        mock_context = TestSessionContext("test", 1)

        client = LaunchableClient(
            "base_url", "org_name", "wp_name", "token", mock_requests, mock_subprocess, mock_context)

        mock_component1 = MagicMock(name="test_path_component1")
        mock_component1.to_body.return_value = {
            "type": "file", "name": "test1.py"}

        mock_component2 = MagicMock(name="test_path_component2")
        mock_component2.to_body.return_value = {
            "type": "file", "name": "test2.py"}

        events = [
            CaseEvent([mock_component1], 0.1,
                      CaseEvent.TEST_PASSED, "stdout1", "stderr1"),
            CaseEvent([mock_component2], 0.2,
                      CaseEvent.TEST_FAILED, "stdout2", "stderr2")
        ]

        client.upload_events(events)

        expected_url = "base_url/intake/organizations/org_name/workspaces/wp_name/builds/test/test_sessions/1/events"
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

        mock_requests.post.assert_called_once_with(
            expected_url, headers=expected_headers, json=expected_body)
        mock_response.raise_for_status.assert_called_once_with()

    def test_finish(self):
        mock_response = MagicMock(name="response")
        mock_requests = MagicMock(name="requests")
        mock_requests.patch.return_value = mock_response

        mock_context = TestSessionContext("test", 1)

        client = LaunchableClient("base_url", "org_name", "wp_name",
                                  "token", mock_requests, MagicMock(name="subprecess"), mock_context)

        client.finish()

        expected_url = "base_url/intake/organizations/org_name/workspaces/wp_name/builds/test/test_sessions/1/close"
        expected_headers = {
            'Content-Type': 'application/json',
            'X-Client-Name': LaunchableClient.CLIENT_NAME,
            'X-Client-Version': __version__,
            'Authorization': 'Bearer token'
        }

        mock_requests.patch.assert_called_once_with(
            expected_url, headers=expected_headers)
        mock_response.raise_for_status.assert_called_once_with()

    def test_parse_option(self):
        option1 = "--target 50% --flavor key=value"
        exp1 = {
            "--target": "50%",
            "--flavor": "key=value",
        }

        option2 = "--split --bin 1/2 --time 1h20m"
        exp2 = {
            "--split": "",
            "--bin": "1/2",
            "--time": "1h20m",
        }

        client = LaunchableClient(None, None, None, None, None, None, None)
        self.assertEqual(client._parse_options(option1), exp1)
        self.assertEqual(client._parse_options(option2), exp2)


class TestTSessionContext(unittest.TestCase):
    def test_get_session(self):
        context = TestSessionContext("test", "1")
        self.assertEqual(context.get_session(), "builds/test/test_sessions/1")

    def test_registered_test_session_true(self):
        context = TestSessionContext("test")
        self.assertTrue(context.registered_test_session())

    def test_registered_test_session_false(self):
        context = TestSessionContext("test", "1")
        self.assertFalse(context.registered_test_session())
