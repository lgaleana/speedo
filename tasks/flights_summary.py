from concurrent.futures import ThreadPoolExecutor

from typing import Any, Dict, List

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


def summarize(flights_json: List[Dict[str, Any]]) -> List[str]:
    with ThreadPoolExecutor() as executor:
        return list(executor.map(summarize_flight, flights_json))
