import unittest
from unittest.mock import MagicMock

from nose_launchable.uploader import UploaderFactory, Uploader
from time import sleep


class TestUploaderFactory(unittest.TestCase):
    def test_prepare(self):
        client = MagicMock(name="client")
        uploader = UploaderFactory.prepare(client)

        self.assertEqual(uploader.client, client)


def _extract_args(m):
    result = []
    for call in m.call_args_list:
        result.extend(call[0][0])

    return result


class TestUploader(unittest.TestCase):
    def test_integration_enqueue_success(self):
        client = MagicMock(name="client")

        uploader = Uploader(client, 0.1, 0.1)
        uploader.start()

        successes = ["1", "2", "3"]

        for s in successes:
            uploader.enqueue_success(s)

        uploader.join()

        self.assertEqual(successes, _extract_args(client.upload_events))

    def test_integration_enqueue_failure(self):
        client = MagicMock(name="client")

        uploader = Uploader(client, 0.1, 0.1)
        uploader.start()

        failures = ["1", "2", "3"]

        for f in failures:
            uploader.enqueue_failure(f)

        uploader.join()

        self.assertEqual(failures, _extract_args(client.upload_events))

    def test_integration_enqueue(self):
        client = MagicMock(name="client")

        uploader = Uploader(client, 0.1, 0.1)
        uploader.start()

        successes = ["s1", "s2", "s3"]

        for s in successes:
            uploader.enqueue_success(s)

        failures = ["f1", "f2", "f3"]

        for f in failures:
            uploader.enqueue_failure(f)

        uploader.join()

        self.assertEqual(["f1", "f2", "f3", "s1", "s2", "s3"], sorted(_extract_args(client.upload_events)))

    def test_integration_enqueue_with_sleep(self):
        client = MagicMock(name="client")

        uploader = Uploader(client, 0.1, 0.1)
        uploader.start()

        successes = ["s1", "s2", "s3"]

        for s in successes:
            uploader.enqueue_success(s)

        failures = ["f1", "f2", "f3"]

        for f in failures:
            uploader.enqueue_failure(f)

        sleep(0.2)

        self.assertEqual(["f1", "f2", "f3", "s1", "s2", "s3"], sorted(_extract_args(client.upload_events)))

        successes = ["s4", "s5", "s6"]

        for s in successes:
            uploader.enqueue_success(s)

        failures = ["f4", "f5", "f6"]

        for f in failures:
            uploader.enqueue_failure(f)

        uploader.join()

        self.assertEqual(["f1", "f2", "f3", "f4", "f5", "f6", "s1", "s2", "s3", "s4", "s5", "s6"], sorted(_extract_args(client.upload_events)))


    def test_integration_enqueue_chunked_batch(self):
        client = MagicMock(name="client")

        uploader = Uploader(client, 0.1, 0.1, 3)
        uploader.start()

        successes = ["s1", "s2", "s3", "s4", "s5", "s6"]

        for s in successes:
            uploader.enqueue_success(s)

        failures = ["f1", "f2", "f3", "f4", "f5", "f6"]

        for f in failures:
            uploader.enqueue_failure(f)

        # send half of events
        sleep(0.2)

        self.assertEqual(["f1", "f2", "f3", "s1", "s2", "s3"], sorted(_extract_args(client.upload_events)))

        uploader.join()

        self.assertEqual(["f1", "f2", "f3", "f4", "f5", "f6", "s1", "s2", "s3", "s4", "s5", "s6"], sorted(_extract_args(client.upload_events)))
