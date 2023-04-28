from typing import Any, Dict

from ai import llm


PROMPT = """
You are a travel assistant.

The following JSON contains a flight route. Summarize it.
"""


def summarize_flight(flight_json: Dict[str, Any]) -> str:
    messages = [
        {"role": "user", "content": PROMPT},
        {"role": "user", "content": str(flight_json)},
    ]
    return llm.next(messages)
