from datetime import datetime
from typing import Any, Dict, List

from ai import llm
from tasks import chat
from tasks.fix_json import fix_request_json
from tasks.flights import get_flights_request
from tasks.flights_summary import summarize_flights
from services.flights import get_routes, search_kiwi
from utils.io import user_input, print_assistant, print_system


MAX_SEARCH_RETRY = 3


def main():
    messages = []

    while True:
        assistant_action = chat.next_action(messages)

        assistant_message = assistant_action["message"]
        messages.append({"role": "assistant", "content": assistant_message})
        print_assistant(assistant_message)

        if assistant_action["action"] != "SEARCH_THE_INTERNET":
            user_message = user_input()
            messages.append({"role": "user", "content": user_message})
        else:
            print_system("\n[Searching...]\n")

            flights_request = get_flights_request(messages)
            flights = _try_search_flights(messages[-2:], flights_request, 1)

            if len(flights) > 0:
                print_system("\n[Found flights. Summarizing...]\n")

                flights_summary = summarize_flights(get_routes(flights))
                for json, flight in zip(flights, flights_summary):
                    print_assistant(f"\n{flight}\nURL: {json['deep_link']}")
            else:
                print_assistant("Sorry. I was unable to find any flights.")
            break


def _try_search_flights(
    messages: List[Dict[str, str]], flights_request: Dict[str, Any], retry: int
) -> List[Dict[str, Any]]:
    assert retry

    flights_json = "error"
    try:
        flights_json = search_kiwi(flights_request)
        return flights_json["data"]
    except Exception as e:
        print_system(f"Exception: {e}")
        if retry < MAX_SEARCH_RETRY:
            print_system("0mRetrying...")
            flights_request = fix_request_json(messages, str(flights_json))
            return _try_search_flights(messages, flights_request, retry + 1)
        raise e


if __name__ == "__main__":
    main()
