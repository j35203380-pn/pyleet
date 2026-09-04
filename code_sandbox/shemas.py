from pydantic import BaseModel

class ExecutionResult(BaseModel):
    logs: list[str]
    output: str
    exit_code: int
    test_result: list[dict]|None=None
    time_ms: float


class ExecutionRequest(BaseModel):
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
