from typing import Any, Dict, List, Tuple
from llm_watch.lib import FAIL, chain_watch, ChainContext

import tasks as t
from services.flights import search_kiwi
from utils.io import print_system


MAX_SEARCH_TRY = 3


def search(
    conversation: List[Dict[str, str]]
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    with ChainContext(prompt=t.flights.PROMPT, default=FAIL) as c:
        original_request = t.flights.get_request(conversation)
        flights_request = _process_flights_request(original_request)
        flights_json = search_kiwi(flights_request)
        if "data" in flights_json:
            c.accept()
            return flights_request, flights_json["data"]

    return _fix_flights_request(original_request, str(flights_json), 2)


@chain_watch(prompt=t.fix_json.PROMPT)
def _fix_flights_request(
    original_request: Dict[str, Any], error: str, retry: int
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    while True:
        print_system(f"Exception: {error}")
        print_system("0mRetrying...")

        fixed_request = t.fix_json.fix_request(str(original_request), str(error))
        flights_request = _process_flights_request(fixed_request)
        flights_json = search_kiwi(flights_request)

        try:
            return flights_request, flights_json["data"]
        except KeyError as e:
            if retry <= MAX_SEARCH_TRY:
                original_request = fixed_request
                error = str(flights_json)
                retry += 1
            raise e


def _process_flights_request(original_request: Dict[str, Any]) -> Dict[str, Any]:
    flights_request = {**original_request}
    flights_request["date_to"] = original_request["date_from"]
    if "return_from" in original_request:
        flights_request["return_to"] = original_request["return_from"]
    flights_request["limit"] = 3
    return flights_request
