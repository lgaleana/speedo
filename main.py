import json
from datetime import datetime
from typing import List

from agents.flights import get_flights, process_flights_json
from agents.flights_summary import summarize_response_json
from chat.api import chat_call
from prompts import chat_prompt


messages = []


def main():
    today = datetime.now().strftime("%B %d, %Y")
    initial_prompt = f"{chat_prompt}\nToday is {today}\nSay hi."
    messages.append({"role": "system", "content": initial_prompt})
    assistant_message = chat_call(messages)
    while True:
        print(f"\033[92m{assistant_message}")
        user_message = input("\033[1;34m")
        messages.append({"role": "user", "content": user_message})
        assistant_message = chat_call(messages)
        messages.append({"role": "assistant", "content": assistant_message})

        parsed_assistant_messages = parse_message(assistant_message)
        if len(parsed_assistant_messages) > 1:
            # print(f"\033[92m{parsed_assistant_messages[0]}")
            print(f"\033[0;0m{parsed_assistant_messages}")

            messages_for_flights_agent = messages[:-1]
            messages_for_flights_agent.append(
                {"role": "assistant", "content": parsed_assistant_messages[0]}
            )
            flights_json = get_flights(messages_for_flights_agent)
            flights_summary = summarize_response_json(process_flights_json(flights_json))
            print(f"\033[0;0m{flights_summary}")
            flights = ""
            for json, flight in zip(flights_json, flights_summary):
                flights += f"{flight}\n{json['deep_link']}\n"
            print(f"\033[92m{flights}")
            break


def parse_message(message: str) -> List[str]:
    return message.split("[Search the Internet]")


if __name__ == "__main__":
    main()
