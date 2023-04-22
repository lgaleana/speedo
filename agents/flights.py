import re
import json
from typing import Any, Dict, List

from agents.chat_api import chat_call
from prompts import flights_prompt


def get_flights_request(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    messages.append({"role": "user", "content": flights_prompt})
    assistant_message = chat_call(messages)
    messages.append({"role": "assistant", "content": assistant_message})
    print(f"\033[0;0m{assistant_message}")
    json_request = _parse_assistant_response_for_json(assistant_message)
    print(f"\033[0;0m{json_request}")
    return json_request


def _parse_assistant_response_for_json(message: str) -> Dict[str, Any]:
    """Might throw"""
    match = re.search("```(.*)```", message, re.DOTALL)
    json_request = match.group(0).replace("```", "")  # type: ignore
    json_request = json.loads(json_request)

    json_request["date_to"] = json_request["date_from"]
    if "return_from" in json_request:
        json_request["return_to"] = json_request["return_from"]
    json_request["limit"] = 3

    return json_request
