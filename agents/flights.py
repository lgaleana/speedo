import re
import json
import os
from typing import Any, Dict, List, Optional

import requests

from chat.api import chat_call
from prompts import flights_prompt


MAX_RETRY = 3


def get_flights(messages: List[Dict[str, str]], retry: int = 0):
    return _get_flights(messages, retry)


def _get_flights(messages: List[Dict[str, str]], retry: int):
    assert retry is not None
    try:
        messages.append({"role": "system", "content": flights_prompt})
        assistant_message = chat_call(messages)
        messages.append({"role": "assistant", "content": assistant_message})
        json_request = _parse_model_response_for_json(assistant_message)
        json_request["limit"] = 5
        flights_response = _search_for_flights(json_request)
        return _parse_flights_response(flights_response)
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
            return _get_flights(messages, retry + 1)
        raise e


def _parse_model_response_for_json(message: str) -> Optional[Dict[str, str]]:
    match = re.search("```(.*)```", message, re.DOTALL)
    if match.group(0):
        request = match.group(0).replace("```", "")
        print(f"\033[0;0m{request}")
        return json.loads(request)
    return None


def _search_for_flights(payload: Dict[str, str]):
    print(f"\033[0;0m{payload}")
    BASE_URL = "https://api.tequila.kiwi.com/v2/search?"

    response = requests.get(
        BASE_URL,
        params=payload,
        headers={
            "accept": "application/json",
            "apikey": os.environ["KIWI"],
        },
    )
    print(f"\033[0;0m{response.json()}")
    return response.json()


def _parse_flights_response(json_response: Dict[str, Any]) -> Dict[str, Any]:
    response = [{"route": flight["route"]} for flight in json_response["data"]]
    print(f"\033[0;0m{response}")
    return response
