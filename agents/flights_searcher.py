from typing import Any, Dict, List, Tuple

import tasks as t
from services.flights import search_kiwi
from utils.io import print_system


MAX_SEARCH_RETRY = 3


def search(
    conversation: List[Dict[str, str]]
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    flights_request = t.flights.get_request(conversation)
    return _try_search_flights(flights_request, 1)


def _try_search_flights(
    original_request: Dict[str, Any], retry: int
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    flights_request = {**original_request}
    flights_request["date_to"] = original_request["date_from"]
    if "return_from" in original_request:
        flights_request["return_to"] = original_request["return_from"]
    flights_request["limit"] = 3

    flights_json = None
    try:
        flights_json = search_kiwi(flights_request)
        return flights_request, flights_json["data"]
    except Exception as e:
        error = flights_json if flights_json else e
        print_system(f"Exception: {error}")
        if retry <= MAX_SEARCH_RETRY:
            print_system("0mRetrying...")
            fixed_request = t.fix_json.fix_request(str(original_request), str(error))
            return _try_search_flights(fixed_request, retry + 1)
        raise e
