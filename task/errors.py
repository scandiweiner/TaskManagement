# Abstract
class Error(Exception):
    pass


class UserAlreadyHasOpenTask(Error):
    pass


class TaskWasCheckedOut(Error):
    pass


BAD_REQUEST = 'bad_request'
USER_ALREADY_HAS_AN_OPEN_TASK = 'user_already_has_an_open_task'
TASK_WAS_CHECKED_OUT = 'task_was_checked_out'
