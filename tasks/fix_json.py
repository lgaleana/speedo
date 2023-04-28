from typing import Any, Dict, List

from ai import llm
from utils.io import print_system
from tasks.flights import parse_assistant_response_for_json


PROMPT = """
The JSON request provided produced the following error. Please fix it:
"""
MAX_RETRY = 3


def fix_request_json(messages: List[Dict[str, str]], error: str) -> Dict[str, Any]:
    messages.append({"role": "system", "content": PROMPT})
    messages.append({"role": "system", "content": error})
    print_system(messages)

    assistant_message = llm.next(messages)
    messages.append({"role": "assistant", "content": assistant_message})
    print_system(assistant_message)

    json_request = parse_assistant_response_for_json(assistant_message)
    print_system(json_request)
    return json_request
