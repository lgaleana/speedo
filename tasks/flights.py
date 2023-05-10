import re
import json
from datetime import datetime
from typing import Any, Dict, List

from ai import llm
from utils.io import print_system


MAX_RETRY = 3


PROMPT = """
Today is {today}.

API documentation:
- fly_from (required): Airport code.
- fly_to: Airport code.
- date_from (required): Departure date (dd/mm/yyyy).
- return_from: Return date (dd/mm/yyyy).
- sort: Sorts the results by quality, price, date or duration. Price is the default value.
- max_stopovers: Max number of stopovers per itinerary.  Use 'max_stopovers=0' for direct flights only.

Based on the conversation above, build a JSON request for the API.

Break this apart into steps:
1. First, summarize the conversation.
2. Then, make the math for the dates.
3. Reflect if you need to include max_stopovers. Include it only if necessary.
4. List only the necessary fields to include.
5. Build the `JSON` request only with necessary fields.

```
JSON request
```
"""


def get_request(conversation: List[Dict[str, str]]) -> Dict[str, Any]:
    today = datetime.now().strftime("%A %B %d, %Y")
    flights_prompt = PROMPT.format(today=today)
    messages = [{"role": "system", "content": flights_prompt}]

    assistant_message = llm.next(conversation + messages)
    print_system(assistant_message)

    return parse_assistant_response_for_json(assistant_message)


def parse_assistant_response_for_json(message: str) -> Dict[str, Any]:
    # Might throw
    message.replace("```json", "```")
    match = re.search("```(.*)```", message, re.DOTALL)
    json_request = match.group(0).replace("```", "")  # type: ignore
    return json.loads(json_request)
