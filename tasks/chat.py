from datetime import datetime
from typing import Dict, List

from ai import llm


COMMAND = "[SEARCH THE INTERNET]"

PROMPT = """
You are a travel assistant. You have access to the internet.
Your goal is to help clients find the best flight tickets, catered to their needs.

Break this apart into 3 TASKS.

TASK 1
- Understand the client preferences.
- Ask one question at a time.
- Be very efficient in communicating. We don't want to waste time.

TASK 2
- Reflect if you're ready to search the internet.
- Make no assumptions. You must always search the internet to get any information about flights.

TASK 3
- Make no assumptions. To search the internet, you must always use the following command:

`{command}`

Today is {today}. Say hi.
"""


def next_action(conversation: List[Dict[str, str]]) -> Dict[str, str]:
    today = datetime.now().strftime("%A %B %d, %Y")
    chat_prompt = PROMPT.format(command=COMMAND, today=today)
    messages = [{"role": "system", "content": chat_prompt}]

    return _parse_assistant_message(llm.next(messages + conversation))


def _parse_assistant_message(assistan_message: str) -> Dict[str, str]:
    parsed_assistant_message = assistan_message.split(COMMAND)

    if len(parsed_assistant_message) > 1:
        message = parsed_assistant_message[0].replace("`", "").strip()
        return {
            "action": "SEARCH_THE_INTERNET",
            "message": message,
        }
    return {
        "action": "GET_USER_FEEDBACK",
        "message": assistan_message,
    }
