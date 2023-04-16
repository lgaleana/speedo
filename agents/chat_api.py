import os
from typing import Any, Dict, List

import openai


MODEL = "gpt-3.5-turbo"
openai.api_key = os.environ["OPENAI_KEY_PERSONAL"]


def openai_call(messages: List[Dict[str, str]], model: str = MODEL) -> Dict[str, Any]:
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.6,
    )
    return response  # type: ignore


def chat_call(messages: List[Dict[str, str]], model: str = MODEL) -> str:
    return openai_call(messages, model)["choices"][0]["message"]["content"]
