import re
import json
from typing import Any, Dict, List, Optional

from agents.chat_api import chat_call
from prompts import flights_prompt


MAX_RETRY = 3


def get_flights_request_json(
    messages: List[Dict[str, str]], retry: int = 0
) -> Dict[str, Any]:
    return _get_flights_request(messages, retry)  # type: ignore


def _get_flights_request(
    messages: List[Dict[str, str]], retry: int
) -> Optional[Dict[str, Any]]:
    assert retry is not None
    try:
        messages.append({"role": "system", "content": flights_prompt})
        assistant_message = chat_call(messages)
        messages.append({"role": "assistant", "content": assistant_message})
        json_request = _parse_assistant_response_for_json(assistant_message)
        json_request["limit"] = 5  # type: ignore
        return json_request
    except Exception as e:
        print(f"\033[0;0mException: {e}")
        if retry < MAX_RETRY:
            print("\033[0;0mRetrying...")
            messages.append(
                {
                    "role": "system",
                    "content": "Previous JSON request produced the following error {e}. Please fix",
                }
            )
            return _get_flights_request(messages, retry + 1)
        raise e


def _parse_assistant_response_for_json(message: str) -> Optional[Dict[str, Any]]:
    """Might throw"""
    match = re.search("```(.*)```", message, re.DOTALL)
    request = match.group(0).replace("```", "")  # type: ignore
    print(f"\033[0;0m{request}")
    return json.loads(request)
