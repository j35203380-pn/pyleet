from msgspec import Struct
from enum import Enum

class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"        
    WRONG_ANSWER = "wrong_answer" 
    RUNTIME_ERROR = "runtime_error"  
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded" 



class ExecutionDocker(Struct):
    logs: list[str]
    output: str
    exit_code: int
    time_ms: float
    test_result: list[dict]|None=None

class ExecutionResult(ExecutionDocker):
    status:SubmissionStatus=SubmissionStatus.PENDING


class ExecutionRequest(Struct):
    mode: str
    code: str
    method_name: str
    test_cases: list[dict]
    



ConfDcoker={
            "Image": "python:3.11-slim",
            "Cmd": ["python", "-"],
            "OpenStdin": True,
            "StdinOnce": True,
            "HostConfig": {
                "Memory": 128 * 1024 * 1024,
                "NanoCpus": 500_000_000,
                "PidsLimit": 64,
                "NetworkMode": "none",
                "ReadonlyRootfs": True,
                "Tmpfs": {"/tmp": "rw,noexec,nosuid,size=64m"},
                "CapDrop": ["ALL"],
                "SecurityOpt": ["no-new-privileges:true"],
            },
            "User": "1000:1000",
        }
