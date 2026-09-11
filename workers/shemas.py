from msgspec import Struct
from enum import Enum


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"        
    WRONG_ANSWER = "wrong_answer" 
    RUNTIME_ERROR = "runtime_error"  
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded" 



class DifficultyLevel(str,Enum):
    EASY='EASY'
    MEDIUM='MEDIUM'
    HARD='HARD'

    


class SubmissionUpdate(Struct):
    status: SubmissionStatus
    exit_code: int
    output: str
    time_ms: float




class ExecutionResult(Struct):
    logs: list[str]
    output: str
    exit_code: int
    time_ms: float
    status: SubmissionStatus
    test_result: list[dict] | None = None

