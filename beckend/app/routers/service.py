from app.database.models import Task
from app.routers.repositories.shemas import ExecutionReq





def message_service(task :Task,mode: str,submission: str):
    message=ExecutionReq(
            mode=mode,
            code=submission,
            method_name=task.method_name,
            test_cases=task.test_cases
        )
    return message

