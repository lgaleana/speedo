from typing import Dict, List, Optional
import re
import json

from chat.api import chat_call
from prompts import flights_prompt


def generate_request_json(messages: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    messages.append({"role": "system", "content": flights_prompt})
    assistant_message = chat_call(messages)
    return parse_message_for_json(assistant_message)


def parse_message_for_json(message: str) -> Optional[Dict[str, str]]:
    match = re.search("```(.*)```", message, re.DOTALL)
    if match.group(0):
        return json.loads(match.group(0).replace("```", ""))
    return None
