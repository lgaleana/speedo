import re
import json
from typing import Dict, List, Optional

import requests

from chat.api import chat_call
from prompts import flights_prompt


def generate_request_json(messages: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    messages.append({"role": "system", "content": flights_prompt})
    assistant_message = chat_call(messages)
    json_request = parse_message_for_json(assistant_message)
    json_request["limit"] = 5
    return json_request


def parse_message_for_json(message: str) -> Optional[Dict[str, str]]:
    match = re.search("```(.*)```", message, re.DOTALL)
    if match.group(0):
        request = match.group(0).replace("```", "")
        print(f"\033[0;0m{request}")
        return json.loads(request)
    return None


def search_for_flights(payload: Dict[str, str]):
    print(f"\033[0;0m{payload}")
    BASE_URL = "https://api.tequila.kiwi.com/v2/search?"

    response = requests.get(
        BASE_URL,
        params=payload,
        headers={
            "accept": "application/json",
            "apikey": "1QTVqV0VjqZPZbyiiXl3WenpNSCCmnnE",
        },
    )
    print(f"\033[0;0m{response.json()}")
    return parse_flights_response(response.json())


def parse_flights_response(response):
    return [flight["deep_link"] for flight in response["data"]]