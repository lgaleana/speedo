import datetime
import functools
from io import TextIOWrapper
import os
from typing import Callable, Optional


LOGS_FOLDER = "logs"

SUCCESS = "SUCCESS"
ERROR = "ERROR"
INVALID = "INVALID"

"""
What to test?
1. Whether the llm searches for flights at some point
2. Whether the json request is built correctly for the flights api
3. Wehther the llm captures the requirements correctly
"""


def llm_watch(validator: Optional[Callable] = None):
    def watch(llm_call: Callable):
        log_file = setup_session_file(llm_call)

        @functools.wraps(llm_call)
        def wrapper_watch(*args, **kwargs):
            try:
                output = llm_call(*args, **kwargs)

                if validator:
                    status = validator(output)
                else:
                    status = SUCCESS
                log(log_file, args, kwargs, status, output)

                return output
            except Exception as e:
                log(log_file, args, kwargs, status=ERROR, exception=e)
                raise e

        return wrapper_watch

    return watch


def log(
    session_file: TextIOWrapper,
    args,
    kwargs,
    status: str,
    output=None,
    exception: Optional[Exception] = None,
) -> None:
    args_repr = [repr(a) for a in args]
    kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
    input_str = ",".join(args_repr + kwargs_repr)

    if not exception:
        session_file.write(f"{input_str}\t{output}\t{status}\n")
    else:
        session_file.write(f"{input_str}\t{status}\t{exception}\n")


def validate_with_user_feedback(_) -> str:
    feedback = input("\033[0;0mWas this interaction successful? (y/n) ").strip().lower()
    if feedback == "n":
        return INVALID
    return SUCCESS


def setup_session_file(llm_call: Callable) -> TextIOWrapper:
    if not os.path.exists(LOGS_FOLDER):
        os.mkdir(LOGS_FOLDER)

    module_path = llm_call.__module__.replace(".", "_")
    llm_call_folder = f"{LOGS_FOLDER}/{module_path}_{llm_call.__name__}"
    if not os.path.exists(llm_call_folder):
        os.mkdir(llm_call_folder)

    now = datetime.datetime.now()
    session_file_name = now.strftime("%Y_%m_%d__%H_%M_%S.txt")
    return open(f"{llm_call_folder}/{session_file_name}", "w+")
