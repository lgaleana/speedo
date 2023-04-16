from datetime import datetime
from typing import Dict, List

from agents.flights import search_for_flights
from agents.flights_summary import summarize_flights
from agents.chat_api import chat_call
from prompts import chat_prompt
from services.flights import process_flights_json


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
        messages.append({"role": "assistant", "content": assistant_message})

        # Parse whether an action needs to be taken
        parsed_assistant_messages = parse_assistant_message(assistant_message)
        if len(parsed_assistant_messages) > 1:
            # print(f"\033[92m{parsed_assistant_messages[0]}")
            print(f"\033[0;0m{parsed_assistant_messages}")

            # Massage context
            messages_for_flights_agent = messages[1:-1]
            messages_for_flights_agent.append(
                {"role": "assistant", "content": parsed_assistant_messages[0]}
            )

            search_flights(messages_for_flights_agent)
            break


def parse_assistant_message(message: str) -> List[str]:
    return message.split("[SEARCHING THE INTERNET]")


def search_flights(messages_for_flights_agent: List[Dict[str, str]]) -> None:
    flights = search_for_flights(messages_for_flights_agent)
    flights_summary = summarize_flights(process_flights_json(flights))
    print(f"\033[0;0m{flights_summary}")

    # Display results
    flight_results = ""
    for json, flight in zip(flights, flights_summary):
        flight_results += f"{flight}\n{json['deep_link']}\n"
    print(f"\033[92m{flight_results}")


if __name__ == "__main__":
    main()
