import os
from typing import Any, Dict, List

import requests


def search_for_flights(payload: Dict[str, str]):
    print(f"\033[0;0m{payload}")
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
    return response.json()["data"]


def process_flights_json(json_response: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    response = [{"route": flight["route"]} for flight in json_response]
    print(f"\033[0;0m{response}")
    return response
