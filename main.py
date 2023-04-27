from datetime import datetime
from typing import Any, Dict, List

from agents.flights import get_flights_request
from agents.flights_summary import summarize_flights
from lib import llm
from prompts import chat_prompt
from services.flights import get_routes, search_kiwi
from utils.io import user_input, print_assistant, print_system


MAX_SEARCH_RETRY = 3


messages = []


def main():
    # Initial prompting
    today = datetime.now().strftime("%A %B %d, %Y")
    messages.append({"role": "system", "content": chat_prompt})
    messages.append({"role": "system", "content": f"Today is {today}\nSay hi."})
    assistant_message = llm.next(messages)
    messages.append({"role": "assistant", "content": assistant_message})

    # Chat loop
    while True:
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
            print_system("[Searching...]\n\n")

            _search_flights(messages)
            break

        messages.append({"role": "assistant", "content": assistant_message})


def _parse_assistant_message(message: str) -> List[str]:
    return message.split("[SEARCH THE INTERNET]")


def _search_flights(messages: List[Dict[str, str]]) -> None:
    flights = _try_search_flights(messages, 1)

    if len(flights) > 0:
        flights_summary = summarize_flights(get_routes(flights))
        print_system(flights_summary)

        # Display results
        flight_results = ""
        for json, flight in zip(flights, flights_summary):
            flight_results += f"{flight}\nURL: {json['deep_link']}\n\n"
        print_assistant("I found the following routes:\n")
        print_assistant(flight_results)
    else:
        print_assistant("Sorry. I was unable to find any flights.")


def _try_search_flights(
    messages: List[Dict[str, str]], retry: int
) -> List[Dict[str, Any]]:
    assert retry

    flights_request = get_flights_request(messages)
    flights_json = "error"
    try:
        flights_json = search_kiwi(flights_request)
        return flights_json["data"]
    except Exception as e:
        print_system(f"Exception: {e}")
        if retry < MAX_SEARCH_RETRY:
            print_system("0mRetrying...")
            messages.append(
                {
                    "role": "system",
                    "content": f"Previous JSON request produced the following error :: {flights_json}. Please fix",
                }
            )
            return _try_search_flights(messages, retry + 1)
        raise e


if __name__ == "__main__":
    main()
