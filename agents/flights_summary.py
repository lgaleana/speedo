from typing import Any, Dict, List

from agents.chat_api import chat_call
from prompts import flights_summary_prompt


def summarize_response_json(response_json: List[Dict[str, Any]]) -> List[str]:
    prompt = f"{flights_summary_prompt}\n\n{response_json}"
    messages = [{"role": "system", "content": prompt}]
    model_response = chat_call(messages)
    return model_response.split("\n")