from typing import Any, Dict

from chat.api import chat_call
from prompts import flights_summary_prompt


def summarize_response_json(response_json: Dict[str, Any]) -> str:
    prompt = f"{flights_summary_prompt}\n\n{response_json}"
    messages = [{"role": "system", "content": prompt}]
    return chat_call(messages)
