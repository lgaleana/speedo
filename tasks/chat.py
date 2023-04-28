from datetime import datetime
from typing import Dict, List

from ai import llm
from tasks.prompts import chat_prompt


STOP = "[SEARCH THE INTERNET]"


def next_action(conversation: List[Dict[str, str]]) -> Dict[str, str]:
    today = datetime.now().strftime("%A %B %d, %Y")
    messages = [
        {"role": "system", "content": chat_prompt},
        {"role": "system", "content": f"Today is {today}\nSay hi."},
    ]

    return _parse_assistant_message(llm.next(messages + conversation))


def _parse_assistant_message(assistan_message: str) -> Dict[str, str]:
    parsed_assistant_message = assistan_message.split(STOP)

    if len(parsed_assistant_message) > 1:
        message = parsed_assistant_message[0].replace("`", "").strip()
        return {
            "action": "SEARCH_THE_INTERNET",
            "message": f"{message}\n\n{STOP}",
        }
    return {
        "action": "GET_USER_FEEDBACK",
        "message": assistan_message,
    }
