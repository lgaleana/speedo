import re
import json
from datetime import datetime
from typing import Any, Dict, List

from ai import llm
from prompts import flights_prompt
from utils.io import print_system


MAX_RETRY = 3


def get_flights_request(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    today = datetime.now().strftime("%A %B %d, %Y")
    messages.append({"role": "system", "content": flights_prompt})
    messages.append({"role": "system", "content": f"Today is {today}."})

    print_system(messages)
    assistant_message = llm.next(messages)
    messages.append({"role": "assistant", "content": assistant_message})
    print_system(assistant_message)

    json_request = parse_assistant_response_for_json(assistant_message)
    print_system(json_request)
    return json_request


def parse_assistant_response_for_json(message: str) -> Dict[str, Any]:
    # Might throw
    message.replace("```json", "```")
    match = re.search("```(.*)```", message, re.DOTALL)
    json_request = match.group(0).replace("```", "")  # type: ignore
    json_request = json.loads(json_request)

    json_request["date_to"] = json_request["date_from"]
    if "return_from" in json_request:
        json_request["return_to"] = json_request["return_from"]
    json_request["limit"] = 3

    return json_request
