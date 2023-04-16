from datetime import datetime
from typing import List

from chat.api import chat_call, base_prompt


messages = []


def main():
    today = datetime.now().strftime("%B %d, %Y")
    initial_prompt = f"{base_prompt}\nToday is {today}\nSay hi."
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
            parsed_messages = "[Search the Internet]".join(parsed_assistant_messages)
            print(f"\033[0;0m{parsed_messages}")
            break
    # Do something


def parse_message(message: str) -> List[str]:
    return message.split("[Search the Internet]")


if __name__ == "__main__":
    main()
