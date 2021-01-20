import datetime


class CaseEvent:
    EVENT_TYPE = "case"
    TEST_PASSED = 1
    TEST_FAILED = 0

    def __init__(self, test_path, duration, status, stdout, stderr):
        self.test_path = test_path
        self.duration = duration
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def to_body(self):
        serialized_test_path = [t.to_body() for t in self.test_path]
        return {
            "type": self.EVENT_TYPE,
            "testPath": serialized_test_path,
            "duration": self.duration,
            "status": self.status,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "data": {"testPath": serialized_test_path},
            "created_at": self.created_at
        }
