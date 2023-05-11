import re
import json
from datetime import datetime
from typing import Any, Dict

from ai import llm
from utils.io import print_system


MAX_RETRY = 3


PROMPT = """
Here is the documentation for a flights API:
- fly_from (required): Airport code.
- fly_to: Airport code.
- date_from (required): Departure date (dd/mm/yyyy).
- return_from: Return date (dd/mm/yyyy).
- sort: Sorts the results by quality, price, date or duration. Price is the default value.
- max_stopovers: Max number of stopovers per itinerary.  Use 'max_stopovers=0' for direct flights only.

Here is a travel itinerary: {itinerary}.

You will build a JSON request from the itinerary.

Do the following:
1. Today is {today}. Make the math for the dates.
2. Reflect if you need to include max_stopovers. Include it only if asbolutely necessary.
3. At the end, build the `JSON` request.
```
JSON request
```

Go ahead.
"""


def get_request(itinerary: str) -> Dict[str, Any]:
    today = datetime.now().strftime("%A %B %d, %Y")
    flights_prompt = PROMPT.format(itinerary=itinerary, today=today)
    messages = [{"role": "user", "content": flights_prompt}]

    assistant_message = llm.next(messages)
    print_system(assistant_message)

    return parse_assistant_response_for_json(assistant_message)


def parse_assistant_response_for_json(message: str) -> Dict[str, Any]:
    # Might throw
    message.replace("```json", "```")
    match = re.search("```(.*)```", message, re.DOTALL)
    json_request = match.group(0).replace("```", "")  # type: ignore
    return json.loads(json_request)
