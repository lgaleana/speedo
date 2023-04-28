from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

from ai import llm
from prompts import flights_summary_prompt


def summarize_flights(flights_json: List[Dict[str, Any]]) -> List[str]:
    with ThreadPoolExecutor() as executor:
        return list(executor.map(summarize_flight, flights_json))


def summarize_flight(flight_json: Dict[str, Any]) -> str:
    prompt = f"{flights_summary_prompt}\n\n{flight_json}"
    messages = [{"role": "user", "content": prompt}]
    return llm.next(messages)
