import datetime
import functools
import inspect
import os
from io import TextIOWrapper
from typing import Callable, Optional


LOGS_FOLDER = "logs"

SUCCESS = "SUCCESS"
ERROR = "ERROR"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"

"""
What to test?
1. Whether the llm searches for flights at some point
2. Whether the json request is built correctly for the flights api
3. Wehther the llm captures the requirements correctly
4. Whether the json is fixed
"""


def llm_watch(validator: Optional[Callable] = None):
    def watch(llm_call: Callable):
        @functools.wraps(llm_call)
        def wrapper_watch(*args, **kwargs):
            wl = WatchLog(llm_call)
            try:
                output = llm_call(*args, **kwargs)
                if validator:
                    wl.set_status(validator(output))
                else:
                    wl.accept()
                wl.log(output=output, *args, **kwargs)
                return output
            except Exception as e:
                wl.invalidate()
                wl.log(exception=e, *args, **kwargs)
                raise e

        return wrapper_watch

    return watch


def validate_with_user_feedback(_) -> str:
    feedback = input("\033[0;0mWas this interaction successful? (y/n) ")
    if feedback.strip().lower() == "n":
        return FAIL
    return SUCCESS


def setup_session_file(path: str) -> TextIOWrapper:
    if not os.path.exists(LOGS_FOLDER):
        os.mkdir(LOGS_FOLDER)

    llm_call_folder = f"{LOGS_FOLDER}/{path}"
    if not os.path.exists(llm_call_folder):
        os.mkdir(llm_call_folder)

    now = datetime.datetime.now()
    session_file_name = now.strftime("%Y_%m_%d.txt")
    return open(f"{llm_call_folder}/{session_file_name}", "a+")


class WatchContext:
    def __init__(
        self, output: Optional[str] = None, validator: Optional[Callable] = None
    ):
        self.validator = validator
        self.wl = WatchLog()

    def __enter__(self):
        previous_frame = inspect.stack()[1]
        self.input = previous_frame.frame.f_locals
        return self.wl

    def __exit__(self, exc_type, exc_value, exc_tb):
        if not exc_type:
            self.wl.log(output=None, **self.input)
        else:
            self.wl.invalidate()
            self.wl.log(output=None, exception=exc_type)


class WatchLog:
    def __init__(self, llm_call: Optional[Callable] = None):
        if llm_call:
            self.path = f"{llm_call.__module__.replace('.', '_')}_{llm_call.__name__}"
        else:
            previous_frame = inspect.stack()[2]
            module_name = inspect.getmodule(previous_frame.frame).__name__.replace(".", "_")  # type: ignore
            function_name = previous_frame.function
            line_no = previous_frame.lineno
            self.path = f"{module_name}_{function_name}_{line_no}"

        self.status = UNKNOWN

    def set_status(self, status: str) -> None:
        self.status = status

    def accept(self) -> None:
        self.set_status(SUCCESS)

    def fail(self) -> None:
        self.set_status(FAIL)

    def invalidate(self) -> None:
        self.set_status(ERROR)

    def log(
        self,
        *args,
        output=None,
        exception: Optional[Exception] = None,
        **kwargs,
    ) -> None:
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        input_str = ",".join(args_repr + kwargs_repr)

        with setup_session_file(self.path) as log_file:
            if not exception:
                log_file.write(f"{self.status}\t{input_str}\t{output}\n")
            else:
                log_file.write(f"{self.status}\t{input_str}\t{exception}\n")
