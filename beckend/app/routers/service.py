from app.database.models import Task
from app.schemas.solution import SolCreate





def message_service(task :Task,mode: str,submission: str):
    message=SolCreate(
            mode=mode,
            code=submission,
            method_name=task.method_name,
            test_cases=task.test_cases
        )
    return message

