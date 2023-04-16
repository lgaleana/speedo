import json
from datetime import datetime
from typing import List

from agents.flights import generate_request_json, search_for_flights
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
            messages_for_flights_agent.append({"role": "assistant", "content": parsed_assistant_messages[0]})
            flights_json = generate_request_json(messages_for_flights_agent)
            
            flights = search_for_flights(flights_json)
            print(f"\033[0;0m{flights}")
            break
    # Do something


def parse_message(message: str) -> List[str]:
    return message.split("[Search the Internet]")


if __name__ == "__main__":
    main()
