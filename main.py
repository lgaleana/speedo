from datetime import datetime
from typing import Any, Dict, List

from agents.flights import get_flights_request
from agents.flights_summary import summarize_flights
from agents.chat_api import chat_call
from prompts import chat_prompt
from services.flights import get_routes, search_kiwi


MAX_SEARCH_RETRY = 3


messages = []


def main():
    # Initial prompting
    today = datetime.now().strftime("%A %B %d, %Y")
    messages.append({"role": "system", "content": chat_prompt})
    messages.append({"role": "system", "content": f"Today is {today}\nSay hi."})
    assistant_message = chat_call(messages)
    messages.append({"role": "assistant", "content": assistant_message})

    # Chat loop
    while True:
        print(f"\033[92m{assistant_message}")
        user_message = input("\033[1;34m")
        messages.append({"role": "user", "content": user_message})
        assistant_message = chat_call(messages)

        # Parse whether an action needs to be taken
        parsed_assistant_message = _parse_assistant_message(assistant_message)
        if len(parsed_assistant_message) > 1:
            print(f"\033[92m{parsed_assistant_message[0]}")
            messages.append(
                {"role": "assistant", "content": parsed_assistant_message[0]}
            )

            _search_flights(messages)
            break

        messages.append({"role": "assistant", "content": assistant_message})


def _parse_assistant_message(message: str) -> List[str]:
    return message.split("[SEARCH THE INTERNET]")


def _search_flights(messages: List[Dict[str, str]]) -> None:
    flights = _try_search_flights(messages, 1)

    if len(flights) > 0:
        flights_summary = summarize_flights(get_routes(flights))
        print(f"\033[0;0m{flights_summary}")

        # Display results
        flight_results = ""
        for json, flight in zip(flights, flights_summary):
            flight_results += f"{flight}\nURL: {json['deep_link']}\n\n"
        print("\033[92mI found the following routes:\n")
        print(f"\033[92m{flight_results}")
    else:
        print("\033[92mSorry. I was unable to find any flights.")


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
        print(f"\033[0;0mException: {e}")
        if retry < MAX_SEARCH_RETRY:
            print("\033[0;0mRetrying...")
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
