from datetime import datetime

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
    # Do something


if __name__ == "__main__":
    main()
