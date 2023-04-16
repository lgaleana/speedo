import re
import json
from typing import Any, Dict, List

from agents.chat_api import chat_call
from prompts import flights_prompt
from services.flights import search_kiwi


MAX_RETRY = 3


def search_for_flights(
    messages: List[Dict[str, str]], retry: int = 0
) -> List[Dict[str, Any]]:
    messages.append({"role": "system", "content": flights_prompt})
    return _try_search_for_flights(messages, retry)


def _try_search_for_flights(
    messages: List[Dict[str, str]], retry: int
) -> List[Dict[str, Any]]:
    assert retry is not None
    try:
        assistant_message = chat_call(messages)
        messages.append({"role": "assistant", "content": assistant_message})
        json_request = _parse_assistant_response_for_json(assistant_message)
        json_request["limit"] = 3
        print(f"\033[0;0m{json_request}")
        flights_json = search_kiwi(json_request)
        return flights_json["data"]
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
            return _try_search_for_flights(messages, retry + 1)
        raise e


def _parse_assistant_response_for_json(message: str) -> Dict[str, Any]:
    """Might throw"""
    match = re.search("```(.*)```", message, re.DOTALL)
    request = match.group(0).replace("```", "")  # type: ignore
    print(f"\033[0;0m{request}")
    return json.loads(request)
