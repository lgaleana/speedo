from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List

from ai import llm
from tasks.fix_json import fix_request_json
from tasks.flights import get_flights_request
from tasks.flights_summary import summarize_flight
from prompts import chat_prompt
from services.flights import get_routes, search_kiwi
from utils.io import user_input, print_assistant, print_system


MAX_SEARCH_RETRY = 3


def main():
    # Initial prompting
    today = datetime.now().strftime("%A %B %d, %Y")
    messages = [{"role": "system", "content": chat_prompt}]
    messages.append({"role": "system", "content": f"Today is {today}\nSay hi."})
    assistant_message = llm.next(messages)

    # Chat loop
    while True:
        messages.append({"role": "assistant", "content": assistant_message})
        print_assistant(assistant_message)
        user_message = user_input()
        messages.append({"role": "user", "content": user_message})
        assistant_message = llm.next(messages)

        # Parse whether an action needs to be taken
        parsed_assistant_message = _parse_assistant_message(assistant_message)
        if len(parsed_assistant_message) > 1:
            print_assistant(f"{parsed_assistant_message[0].strip()}\n")
            messages.append(
                {"role": "assistant", "content": parsed_assistant_message[0].strip()}
            )
            print_system("[Searching...]\n")

            messages = messages[1:]
            flights_request = get_flights_request(messages)
            flights = _search_flights(messages[-2:], flights_request)

            if len(flights) > 0:
                print_system("\n[Flights found. Summarizing...]\n")

                flights_summary = _summarize_flights(get_routes(flights))
                for json, flight in zip(flights, flights_summary):
                    print_assistant(f"\n{flight}\nURL: {json['deep_link']}")
            else:
                print_assistant("Sorry. I was unable to find any flights.")
            break


def _parse_assistant_message(message: str) -> List[str]:
    return message.split("[SEARCH THE INTERNET]")


def _search_flights(
    messages: List[Dict[str, str]], flights_request: Dict[str, Any]
) -> List[Dict[str, Any]]:
    return _try_search_flights(messages, flights_request, 1)


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


def _summarize_flights(flights_json: List[Dict[str, Any]]) -> List[str]:
    with ThreadPoolExecutor() as executor:
        return list(executor.map(summarize_flight, flights_json))


if __name__ == "__main__":
    main()
