import os
from typing import Any, Dict

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
    return response.json()
