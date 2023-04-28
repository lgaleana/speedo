from typing import Any, Dict, List

from ai import llm
from utils.io import print_system
from tasks.prompts import flights_api_prompt
from tasks.flights import parse_assistant_response_for_json


def fix_request(wrong_json_request: str, error: str) -> Dict[str, Any]:
    wrong_json_request = wrong_json_request.replace("'", '"')
    messages = [
        {"role": "user", "content": flights_api_prompt},
        {
            "role": "user",
            "content": f"The following JSON request produced the following error: {error}.",
        },
        {"role": "user", "content": f"```\n{wrong_json_request}\n```"},
        {"role": "user", "content": "Check if the airport codes are correct."},
        {"role": "user", "content": "Then, write the correct JSON."},
        {"role": "user", "content": "```\nJSON\n```"},
    ]

    assistant_message = llm.next(messages)
    print_system(assistant_message)

    json_request = parse_assistant_response_for_json(assistant_message)
    print_system(json_request)
    return json_request
