from config import SubmissionStatus


async def determine_statuse(exit_code,test_results):

    if exit_code!=0:
        if exit_code ==137:
            return SubmissionStatus.TIME_LIMIT_EXCEEDED
        return SubmissionStatus.RUNTIME_ERROR

    if test_results is None:
        return SubmissionStatus.RUNTIME_ERROR

    if all(x['passed'] for x in test_results):
        return SubmissionStatus.ACCEPTED

    return SubmissionStatus.WRONG_ANSWER


