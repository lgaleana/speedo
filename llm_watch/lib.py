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
1. Whether the llm searches for flights at some point -> user validation
2. Whether the json request is built correctly for the flights api -> manual validation
3. Wehther the llm captures the requirements correctly
4. Whether the json is fixed -> no exceptions validation
"""


def chain_watch(prompt: str = UNKNOWN, validator: Optional[Callable] = None):
    def watch(llm_call: Callable):
        @functools.wraps(llm_call)
        def wrapper_watch(*args, **kwargs):
            log = _LogHandler(llm_call)
            log.log_start()
            log.log_prompt(prompt)

            try:
                output = llm_call(*args, **kwargs)

                if validator:
                    log.log_status(validator(output))
                else:
                    log.log_accept()
                log.log_end()

                return output
            except Exception as e:
                log.log_exception(e)
                log.log_end()
                raise e

        return wrapper_watch

    return watch


def validate_with_user_feedback(_) -> str:
    feedback = input("\033[0;0m\nWas this interaction successful? (y/n) ")
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


class ChainContext:
    def __init__(
        self,
        prompt: str = UNKNOWN,
        validator: Optional[Callable] = None,
        default=UNKNOWN,
    ):
        self.log = _LogHandler()
        self.prompt = prompt
        self.validator = validator
        self.status = default

    def __enter__(self):
        self.log.log_start()
        self.log.log_prompt(self.prompt)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if not exc_type:
            self.log.log_status(self.status)
        else:
            self.log.log_exception(exc_type)
        self.log.log_end()

    def accept(self) -> None:
        self.status = SUCCESS


class _LogHandler:
    def __init__(self, llm_call: Optional[Callable] = None):
        if llm_call:
            path = f"{llm_call.__module__.replace('.', '_')}_{llm_call.__name__}"
        else:
            previous_frame = inspect.stack()[2]
            module_name = inspect.getmodule(previous_frame.frame).__name__.replace(".", "_")  # type: ignore
            function_name = previous_frame.function
            line_no = previous_frame.lineno
            path = f"{module_name}_{function_name}_{line_no}"

        self.log_file = setup_session_file(path)

    def log_start(self) -> None:
        now = datetime.datetime.now().strftime("%Y_%m_%d %H:%M:%S")
        self.log_file.write("---CHAIN START---\n")
        self.log_file.write(f"START TIME: {now}\n")

    def log_status(self, status: str) -> None:
        self.log_file.write(f"STATUS: {status}\n")

    def log_accept(self) -> None:
        self.log_file.write(f"STATUS: {SUCCESS}\n")

    def log_exception(self, e: Exception) -> None:
        self.log_file.write(f"EXCEPTION: {e}\n")

    def log_end(self) -> None:
        now = datetime.datetime.now().strftime("%Y_%m_%d %H:%M:%S")
        self.log_file.write(f"END TIME: {now}\n")
        self.log_file.write("---CHAIN END---\n")

    def log_prompt(self, prompt: str) -> None:
        self.log_file.write("START PROMPT\n")
        self.log_file.write(f"{prompt}\n")
        self.log_file.write("END PROMPT\n")
