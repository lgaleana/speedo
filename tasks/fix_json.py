from typing import Any, Dict

from ai import llm
from tasks.flights import parse_assistant_response_for_json
from utils.io import print_system


PROMPT = """
API documentation:
- fly_from (required): Airport code.
- fly_to: Airport code.
- date_from (required): Departure date (dd/mm/yyyy).
- return_from: Return date (dd/mm/yyyy).
- sort: Sorts the results by quality, price, date or duration. Price is the default value.
- max_stopovers: Max number of stopovers per itinerary.  Use 'max_stopovers=0' for direct flights only.

"The following JSON request produced the following error: {error}.
```
{wrong_json_request}
```

Check if the airport codes are correct.
Then, write the correct JSON:
```
JSON
```
"""


def fix_request(wrong_json_request: str, error: str) -> Dict[str, Any]:
    wrong_json_request = wrong_json_request.replace("'", '"')
    messages = [
        {
            "role": "user",
            "content": PROMPT.format(
                error=error, wrong_json_request=wrong_json_request
            ),
        }
    ]

    assistant_message = llm.next(messages)
    print_system(assistant_message)

    json_request = parse_assistant_response_for_json(assistant_message)
    return json_request
