import os
from typing import Any, Dict, List

import requests


def search_kiwi(payload: Dict[str, Any]):
    BASE_URL = "https://api.tequila.kiwi.com/v2/search?"

    response = requests.get(
        BASE_URL,
        params=payload,
        headers={
            "accept": "application/json",
            "apikey": os.environ["KIWI"],
        },
    )
    print(f"\033[0;0m{response.json()}")
    return response.json()


def get_routes(json_response: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    processed_response = [{"route": flight["route"]} for flight in json_response]
    for route in processed_response:
        print(f"\033[0;0m{route}")
    return processed_response
