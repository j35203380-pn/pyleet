from msgspec import Struct


class SubmissCode(Struct):
    code: str




class ExecutionReq(Struct):
    mode: str
    code: str
    method_name: str
    test_cases: list[dict]
