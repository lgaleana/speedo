import re
from datetime import datetime
from typing import Dict, List

from ai import llm


PROMPT = """
You are a travel AI assistant.
Your goal is to help clients find the best flight tickets, catered to their needs.
Go out of your way to really understand and satisfy what the client wants.

To achieve your goal, you can perform the following actions:
1. CHAT[message]: To collect information about the client preferences. Try to collect as much information at once.
2. SEARCH[itinerary]: To search for flight tickets. Use this action once you have collected enough information.

Use the following format:
OBSERVATION: What you see.
ASSISTANT ACTION: An action to perform. Use the correct syntax from above.

OBSERVATION: This is the beginning of the conversation.
{conversation}
"""


def next_action(conversation: List[Dict[str, str]]) -> Dict[str, str]:
    today = datetime.now().strftime("%A %B %d, %Y")
    chat_prompt = PROMPT.format(today=today, conversation=_parse_input(conversation))
    messages = [{"role": "user", "content": chat_prompt}]

    return _parse_assistant_message(llm.next(messages))


def _parse_input(conversation: List[Dict[str, str]]) -> str:
    conversation_str = ""
    for message in conversation:
        if message["role"] == "client":
            conversation_str += f"\nOBSERVATION: CLIENT SAYS: {message['message']}\n"
        else:
            conversation_str += (
                f"ASSISTANT ACTION: {message['action']}[{message['message']}]\n"
            )
    return conversation_str


def _parse_assistant_message(assistan_message: str) -> Dict[str, str]:
    # Might throw
    match = re.search(r"ASSISTANT ACTION: (CHAT|SEARCH)\[(.*)\]", assistan_message)
    action = match.group(1)  # type: ignore
    message = match.group(2)  # type: ignore

    if action.startswith("SEARCH"):
        return {
            "action": "SEARCH",
            "message": message,
        }
    return {
        "action": "CHAT",
        "message": message,
    }
