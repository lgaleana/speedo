from concurrent.futures import ThreadPoolExecutor

from typing import Any, Dict, List

from ai import llm


PROMPT = """
You are a travel assistant.

The following JSON contains data about a flight. Summarize it.

Constraints:
1. Mention the most helpful information.
2. Turn seconds into hours.
3. Don't mention the word JSON.

{flight_json}
"""


def summarize_flight(flight_json: Dict[str, Any]) -> str:
    messages = [{"role": "user", "content": PROMPT.format(flight_json=flight_json)}]
    return llm.next(messages, temperature=0.4)


def summarize(flights_json: List[Dict[str, Any]]) -> List[str]:
    with ThreadPoolExecutor() as executor:
        return list(executor.map(summarize_flight, flights_json))
