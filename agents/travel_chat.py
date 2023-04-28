from typing import Any, Dict, List

import tasks as t
from services.flights import get_routes, search_kiwi
from utils.io import user_input, print_assistant, print_system


MAX_SEARCH_RETRY = 3


def chat():
    converation = []

    while True:
        assistant_action = t.chat.next_action(converation)

        assistant_message = assistant_action["message"]
        converation.append({"role": "assistant", "content": assistant_message})
        print_assistant(assistant_message)

        if assistant_action["action"] != "SEARCH_THE_INTERNET":
            user_message = user_input()
            converation.append({"role": "user", "content": user_message})
        else:
            print_system("\n[Searching...]\n")

            flights_request = t.flights.get_request(converation)
            flights = _try_search_flights(flights_request, 1)

            if len(flights) > 0:
                print_system("\n[Found flights. Summarizing...]")

                flights_summary = t.flights_summary.summarize(get_routes(flights))
                for json, flight in zip(flights, flights_summary):
                    print_assistant(f"\n{flight}\nURL: {json['deep_link']}")
            else:
                print_assistant("Sorry. I was unable to find any flights.")
            break


def _try_search_flights(
    flights_request: Dict[str, Any], retry: int
) -> List[Dict[str, Any]]:
    assert retry

    flights_json = "error"
    try:
        flights_json = search_kiwi(flights_request)
        return flights_json["data"]
    except Exception as e:
        print_system(f"Exception: {e}")
        if retry <= MAX_SEARCH_RETRY:
            print_system("0mRetrying...")
            flights_request = t.fix_json.fix_request(
                str(flights_request), str(flights_json)
            )
            return _try_search_flights(flights_request, retry + 1)
        raise e
