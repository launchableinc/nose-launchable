import os
import queue
import threading
from time import sleep

from nose_launchable.protecter import protect


class UploaderFactory:
    SUCCESS_REPORT_INTERVAL_KEY = "LAUNCHABLE_SUCCESS_REPORT_INTERVAL"
    FAILURE_REPORT_INTERVAL_KEY = "LAUNCHABLE_FAILURE_REPORT_INTERVAL"

    DEFAULT_SUCCESS_REPORT_INTERVAL = 3
    DEFAULT_FAILURE_REPORT_INTERVAL = 2

    @classmethod
    def prepare(cls, client):
        return Uploader(client, cls._get_success_interval(), cls._get_failure_interval())

    @classmethod
    def _get_success_interval(cls):
        return os.getenv(cls.SUCCESS_REPORT_INTERVAL_KEY) or cls.DEFAULT_SUCCESS_REPORT_INTERVAL

    @classmethod
    def _get_failure_interval(cls):
        return os.getenv(cls.FAILURE_REPORT_INTERVAL_KEY) or cls.DEFAULT_FAILURE_REPORT_INTERVAL


DEFAULT_MAX_BATCH_SIZE = 500

class Uploader:

    def __init__(self, client, success_interval, failure_interval, max_batch_size=DEFAULT_MAX_BATCH_SIZE):
        self.client = client

        self.success_queue = queue.Queue()
        self.failure_queue = queue.Queue()

        self.success_worker = threading.Thread(target=self._worker, args=(self.success_queue, success_interval,))
        self.failure_worker = threading.Thread(target=self._worker, args=(self.failure_queue, failure_interval,))

        self.max_batch_size = max_batch_size

    def start(self):
        self.success_worker.start()
        self.failure_worker.start()

    def enqueue_success(self, result):
        self.success_queue.put(result)

    def enqueue_failure(self, result):
        self.failure_queue.put(result)

    def join(self):
        # Do not join the queues, otherwise the main thread gets stuck if one of the worker fails
        # self.success_queue.join()
        # self.failure_queue.join()

        self.success_queue.put(None)
        self.failure_queue.put(None)

        self.success_worker.join()
        self.failure_worker.join()

    # Main thread cannot catch child thread's errors
    @protect
    def _worker(self, q, interval):
        wait = True

        while wait:
            sleep(interval)

            size = min(q.qsize(), self.max_batch_size)

            results = []
            for _ in range(size):
                item = q.get()

                if item is None:
                    wait = False
                    break

                results.append(item)
                q.task_done()

            if len(results) != 0:
                self._upload(results)

    def _upload(self, events):
        self.client.upload_events(events)
