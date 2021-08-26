import os
import subprocess
import shlex

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
    def prepare(cls, build_number, session):
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

        if build_number:
            context = TestSessionContext(build_number)
        else:
            _, bn, _, ts = session.split("/")
            context = TestSessionContext(bn, ts)

        return LaunchableClient(url, org, wp, token, http, subprocess, context)

    @classmethod
    def _parse_options(cls):
        token = os.environ.get(cls.TOKEN_KEY)
        if token is None:
            raise Exception("%s not set" % cls.TOKEN_KEY)

        _, user, _ = token.split(":", 2)
        org, workplace = user.split("/", 1)

        return cls._get_base_url(), org, workplace, token

    @classmethod
    def _get_base_url(cls):
        return os.getenv(cls.BASE_URL_KEY) or cls.DEFAULT_BASE_URL


class LaunchableClient:
    CLIENT_NAME = "nose-launchable"

    def __init__(self, base_url, org_name, workspace_name, token, http, process, context):
        self.base_url = base_url
        self.org_name = org_name
        self.workspace_name = workspace_name
        self.token = token
        self.http = http
        self.process = process
        self.test_session_context = context

    def start(self):
        if not self.test_session_context.registered_test_session():
            return

        url = "{}/intake/organizations/{}/workspaces/{}/builds/{}/test_sessions".format(
            self.base_url,
            self.org_name,
            self.workspace_name,
            self.test_session_context.build_number
        )

        res = self.http.post(url, headers=self._headers())
        logger.debug("Response status code: {}".format(res.status_code))
        res.raise_for_status()

        response_body = res.json()
        logger.debug("Response body: {}".format(response_body))

        self.test_session_context.test_session_id = response_body["id"]

    def subset(self, test_names, options, target):

        opts = {}
        if options is not None:
            # split subset
            if "--bin" in options:
                return self.split_subset(test_names, options)

            opts = self._parse_options(options)
        else:
            opts["--target"] = target + "%"

        # launchable subset command returns a list of test names splitted by \n
        order = self._subset(test_names, opts).rstrip("\n").split("\n")

        logger.debug("Subset test order: {}".format(order))

        return order

    def split_subset(self, test_names, options):
        opts = self._parse_options(options)

        opts_for_subset = opts.copy()
        del opts_for_subset["--bin"]
        opts_for_subset["--split"] = ""

        subset_id = self._subset(
            test_names, opts_for_subset).rstrip("\n")

        split_subset_cmd = ['launchable',
                            'split-subset', '--subset-id', subset_id]

        split_subset_cmd.extend(['--bin', opts['--bin']])
        split_subset_cmd.append("file")

        logger.debug("Split-Subset command: {}".format(split_subset_cmd))

        proc = self.process.run(
            split_subset_cmd,
            encoding='utf-8',
            stdout=self.process.PIPE,
            stderr=self.process.PIPE
        )

        if proc.returncode != 0:
            raise RuntimeError(
                "launchable split subset command fails. stdout: {}, stderr: {}", proc.stdout, proc.stderr)

        # launchable split subset command returns a list of test names splitted by \n
        order = proc.stdout.rstrip("\n").split("\n")

        logger.debug("Split-Subset test order: {}".format(order))

        return order

    """
    @param: options Require dictionary that returned _parse_options method
    """

    def _subset(self, test_names, options):
        subset_cmd = ['launchable', 'subset', '--session',
                      self.test_session_context.get_session()]

        for k, v in options.items():
            if v == "":  # bool option
                subset_cmd.append(k)
                continue
            subset_cmd.extend([k, v])

        subset_cmd.append("file")

        logger.debug("Subset command: {}".format(subset_cmd))

        proc = self.process.run(
            subset_cmd,
            input="\n".join(test_names),
            encoding='utf-8',
            stdout=self.process.PIPE,
            stderr=self.process.PIPE
        )

        if proc.returncode != 0:
            raise RuntimeError(
                "launchable subset command fails. stdout: {}, stderr: {}", proc.stdout, proc.stderr)

        return proc.stdout

    def upload_events(self, events):
        url = "{}/intake/organizations/{}/workspaces/{}/{}/events".format(
            self.base_url,
            self.org_name,
            self.workspace_name,
            self.test_session_context.get_session(),
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
            self.test_session_context.get_session(),
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

    def _parse_options(self, option_str):
        args = shlex.split(option_str)
        option = {}
        for k, v in zip(args, args[1:]+["--"]):
            if not k.startswith("-"):
                continue

            if v.startswith("-"):  # bool flag
                option[k] = ""
            else:
                option[k] = v

        return option


class TestSessionContext:
    def __init__(self, build_number, test_session_id=None):
        self.build_number = build_number
        self.test_session_id = test_session_id
    
    def get_session(self):
        return "builds/{}/test_sessions/{}".format(self.build_number, self.test_session_id)

    def registered_test_session(self):
        return self.test_session_id is None
