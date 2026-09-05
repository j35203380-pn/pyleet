from config import SubmissionStatus
from app.database.models import Task
from app.database.shemas.task_shemas import ExecutionRequest,SubmissionCreate



def determine_statuse(exit_code,test_results):

    if exit_code!=0:
        if exit_code ==137:
            return SubmissionStatus.TIME_LIMIT_EXCEEDED
        return SubmissionStatus.RUNTIME_ERROR

    if test_results is None:
        return SubmissionStatus.RUNTIME_ERROR

    if all(x['passed'] for x in test_results):
        return SubmissionStatus.ACCEPTED

    return SubmissionStatus.WRONG_ANSWER




def message_service(task :Task,mode: str,submission: SubmissionCreate):
    message=ExecutionRequest(
            mode=mode,
            code=submission.code,
            method_name=task.method_name,
            test_cases=task.test_cases
        )
    return message

