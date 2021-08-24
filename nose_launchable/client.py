import os
import subprocess

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from nose_launchable.log import logger
from nose_launchable.version import __version__


class LaunchableClientFactory:
    BASE_URL_KEY = "LAUNCHABLE_BASE_URL"
    TOKEN_KEY = "LAUNCHABLE_TOKEN"

    DEFAULT_BASE_URL = "https://api.mercury.launchableinc.com"

    @classmethod
    def prepare(cls):
        url, org, wp, token = cls._parse_options()
        strategy = Retry(
            total=3,
            method_whitelist=["GET", "PUT", "PATCH", "DELETE"],
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=2
        )

        adapter = HTTPAdapter(max_retries=strategy)
        http = Session()
        http.mount("http://", adapter)
        http.mount("https://", adapter)

        return LaunchableClient(url, org, wp, token, http, subprocess)

    @classmethod
    def _parse_options(cls):
        token = os.environ.get(cls.TOKEN_KEY)
        if token is None:
            raise Exception("%s not set"%cls.TOKEN_KEY)

        _, user, _ = token.split(":", 2)
        org, workplace = user.split("/", 1)

        return cls._get_base_url(), org, workplace, token

    @classmethod
    def _get_base_url(cls):
        return os.getenv(cls.BASE_URL_KEY) or cls.DEFAULT_BASE_URL


class LaunchableClient:
    CLIENT_NAME = "nose-launchable"

    def __init__(self, base_url, org_name, workspace_name, token, http, process):
        self.base_url = base_url
        self.org_name = org_name
        self.workspace_name = workspace_name
        self.token = token
        self.http = http
        self.process = process
        self.build_number = None
        self.test_session_context = None

    def start(self, build_number):
        self.build_number = build_number
        url = "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions".format(
            self.base_url,
            self.org_name,
            self.workspace_name,
            self.build_number
        )

        res = self.http.post(url, headers=self._headers())
        logger.debug("Response status code: {}".format(res.status_code))
        res.raise_for_status()

        response_body = res.json()
        logger.debug("Response body: {}".format(response_body))

        self.test_session_context = TestSessionContext(
            build_number=build_number, test_session_id=response_body["id"])

    def subset(self, test_names, options, target):
        cmd = ['launchable', 'subset', '--session',
               self.test_session_context.get_build_path()]
        if options is not None:
            cmd.extend([option.strip() for option in options.split(' ')])
            cmd.append('file')
        else:
            cmd.extend(['--target', target + '%', 'file'])

        logger.debug("Subset command: {}".format(cmd))

        proc = self.process.run(
            cmd,
            input="\n".join(test_names),
            encoding='utf-8',
            stdout=self.process.PIPE,
            stderr=self.process.PIPE
        )

        if proc.returncode != 0:
            raise RuntimeError("launchable subset command fails. stdout: {}, stderr: {}", proc.stdout, proc.stderr)

        # launchable subset command returns a list of test names splitted by \n
        order = proc.stdout.rstrip("\n").split("\n")

        logger.debug("Subset test order: {}".format(order))

        return order

    def upload_events(self, events):
        url = "{}/intake/organizations/{}/workspaces/{}/{}/events".format(
            self.base_url,
            self.org_name,
            self.workspace_name,
            self.test_session_context.get_build_path(),
        )

        request_body = self._upload_request_body(events)
        logger.debug("Request body: {}".format(request_body))

        res = self.http.post(url, headers=self._headers(), json=request_body)
        res.raise_for_status()

    def finish(self):
        url = "{}/intake/organizations/{}/workspaces/{}/{}/close".format(
            self.base_url,
            self.org_name,
            self.workspace_name,
            self.test_session_context.get_build_path(),
        )

        res = self.http.patch(url, headers=self._headers())
        res.raise_for_status()

    def _headers(self):
        return {
            'Content-Type': 'application/json',
            'X-Client-Name': self.CLIENT_NAME,
            'X-Client-Version': __version__,
            'Authorization': 'Bearer {}'.format(self.token)
        }

    def _upload_request_body(self, events):
        return {"events": [event.to_body() for event in events]}


class TestSessionContext:
    def __init__(self, build_number=None, test_session_id=None):
        self.build_number = build_number
        self.test_session_id = test_session_id

    def get_build_path(self):
        return "builds/{}/test_sessions/{}".format(self.build_number, self.test_session_id)
