from dataclasses import dataclass


@dataclass(slots=True)
class SolCreate:
    mode: str
    code: str
    method_name: str
    test_cases: list[dict]



@dataclass(slots=True)
class SubPostAdd:
    task_id: int
    user_id: int
    code: str
    message: list[dict]