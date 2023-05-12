from typing import Any, Dict, List, Tuple
from llm_watch.lib import FAIL, chain_watch, ChainContext

import tasks as t
from services.flights import search_kiwi
from utils.io import print_system


MAX_SEARCH_TRY = 2


def search(itinerary: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    with ChainContext(prompt=t.flights.PROMPT, default=FAIL) as c:
        original_request = t.flights.get_request(itinerary)
        flights_request = _process_flights_request(original_request)
        flights_json = search_kiwi(flights_request)

        if "data" in flights_json:
            c.accept()
            return flights_request, _process_flights_data(flights_json["data"])

    return _fix_flights_request(original_request, str(flights_json))


@chain_watch(prompt=t.fix_json.PROMPT)
def _fix_flights_request(
    original_request: Dict[str, Any], error: str
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    retry = 1
    while True:
        print_system(f"(Exception: {error})")
        print_system("(Retrying...)")

        fixed_request = t.fix_json.fix_request(str(original_request), str(error))
        flights_request = _process_flights_request(fixed_request)
        flights_json = search_kiwi(flights_request)

        try:
            return flights_request, _process_flights_data(flights_json["data"])
        except KeyError as e:
            if retry <= MAX_SEARCH_TRY:
                original_request = fixed_request
                error = str(flights_json)
                retry += 1
            else:
                raise e


def _process_flights_request(original_request: Dict[str, Any]) -> Dict[str, Any]:
    flights_request = {**original_request}
    flights_request["date_to"] = original_request["date_from"]
    if "return_from" in original_request:
        flights_request["return_to"] = original_request["return_from"]
    flights_request["limit"] = 3
    flights_request["curr"] = "USD"
    print_system(flights_request)
    return flights_request


def _process_flights_data(flights_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for f in flights_data:
        del f["booking_token"]
    return flights_data
