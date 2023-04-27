import re
import json
from typing import Any, Dict, List

from lib import llm
from prompts import flights_prompt
from utils.io import print_system


MAX_RETRY = 3


def get_flights_request(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    return _try_get_flights_request(messages, 1)


def _try_get_flights_request(messages: List[Dict[str, str]], retry: int) -> Dict[str, Any]:
    assert retry
    
    messages.append({"role": "user", "content": flights_prompt})
    assistant_message = llm.next(messages)
    messages.append({"role": "assistant", "content": assistant_message})
    print_system(assistant_message)
    
    try :
        json_request = _parse_assistant_response_for_json(assistant_message)
        print_system(json_request)
        return json_request
    except Exception as e:
        print_system(f"Exception: {e}")
        if retry < MAX_RETRY:
            print_system("0mRetrying...")
            messages.append(
                {
                    "role": "system",
                    "content": f"Previous JSON request produced the following error {e}. Please fix",
                }
            )
            return _try_get_flights_request(messages, retry + 1)
        raise e


def _parse_assistant_response_for_json(message: str) -> Dict[str, Any]:
    match = re.search("```(.*)```", message, re.DOTALL)
    json_request = match.group(0).replace("```", "")  # type: ignore
    json_request = json.loads(json_request)

    json_request["date_to"] = json_request["date_from"]
    if "return_from" in json_request:
        json_request["return_to"] = json_request["return_from"]
    json_request["limit"] = 3

    return json_request
