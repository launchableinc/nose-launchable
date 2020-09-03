import json
import os
from collections import defaultdict

import boto3
import requests


class LaunchableClientFactory:
    BASE_URL_KEY = "LAUNCHABLE_REORDERING_BASE_URL"
    ORG_NAME_KEY = "LAUNCHABLE_REORDERING_ORG_NAME"
    WORKPLACE_NAME_KEY = "LAUNCHABLE_REORDERING_WORKPLACE_NAME"
    API_TOKEN_KEY = "LAUNCHABLE_REORDERING_API_TOKEN"

    @classmethod
    def prepare(cls):
        return LaunchableClient(
            os.environ[cls.BASE_URL_KEY],
            os.environ[cls.ORG_NAME_KEY],
            os.environ[cls.WORKPLACE_NAME_KEY],
            os.environ[cls.API_TOKEN_KEY],
            requests,
        )


class LaunchableClient:
    def __init__(self, base_url, org_name, workspace_name, api_token, http):
        self.base_url = base_url
        self.org_name = org_name
        self.workspace_name = workspace_name
        self.api_token = api_token
        self.http = http

    def infer(self, names, template):
        url = "{}/intake/organizations/{}/workspaces/{}/inference".format(
            self.base_url,
            self.org_name,
            self.workspace_name
        )
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(self.api_token)}
        body = self._request_body(names, template)

        res = self.http.post(url, headers=headers, json=body)
        res.raise_for_status()

        return res.json()

    def _request_body(self, tests, template):
        tests_map = defaultdict(set)
        for test in tests:
            tests_map[test["className"]].add(test["name"])

        template_tests = template["tests"]
        matched = []

        for template_test in template_tests:
            cls, name = template_test["className"], template_test["name"]

            if name in tests_map[cls]:
                matched.append(
                    {
                        "buildNumber": template_test["buildNumber"],
                        "className": cls,
                        "name": name,
                        "duration": template_test["duration"],
                        "stdout": template_test["stdout"],
                        "stderr": template_test["stderr"],
                        "status": template_test["status"],
                        "flavors": template_test["flavors"],
                    }
                )

                tests_map[cls].remove(name)

        # Fill the remaining tests with some fictitious values
        # They are most likely new tests
        for cls, names in tests_map.items():
            for name in names:
                matched.append(
                    {
                        "buildNumber": 100,
                        "className": cls,
                        "name": name,
                        "duration": 5,
                        "stdout": "",
                        "stderr": "",
                        "status": "PASSED",
                        "flavors": {},
                    }
                )

        template["tests"] = matched
        return template


class S3ClientFactory:
    AWS_REGION = "us-west-2"
    AWS_ACCESS_KEY_ID_KEY = "LAUNCHABLE_REORDERING_AWS_ACCESS_KEY_ID"
    AWS_SECRET_ACCESS_KEY_KEY = "LAUNCHABLE_REORDERING_AWS_SECRET_ACCESS_KEY"

    @classmethod
    def prepare(cls):
        session = boto3.Session(
            aws_access_key_id=os.environ[cls.AWS_ACCESS_KEY_ID_KEY],
            aws_secret_access_key=os.environ[cls.AWS_SECRET_ACCESS_KEY_KEY],
            region_name=cls.AWS_REGION
        )

        return S3Client(session.resource("s3"))


class S3Client:
    BUCKET_NAME = "launchableinc-pap"
    TEMPLATE_FILE_NAME = "request_template.json"

    def __init__(self, s3):
        self.s3 = s3

    def get_template(self, dir_name):
        obj = self.s3.Object(self.BUCKET_NAME, "{}/{}".format(dir_name, self.TEMPLATE_FILE_NAME))
        return json.loads(obj.get()['Body'].read().decode('utf-8'))
