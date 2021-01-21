class TestPathComponent:
    FILE_TYPE = "file"
    CLASS_TYPE = "class"
    CASE_TYPE = "testcase"

    def __init__(self, type, name):
        self.type = type
        self.name = name

    def to_body(self):
        return {"type": self.type, "name": self.name}
