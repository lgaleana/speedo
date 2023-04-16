import os
import json
from typing import Any, Dict, List

import openai

from prompts import chat_prompt


MODEL = "gpt-3.5-turbo"
openai.api_key = os.environ["OPENAI_KEY_PERSONAL"]


def openai_call(messages: List[Dict[str, str]], model: str = MODEL) -> Dict[str, Any]:
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.6,
    )
    return response


def chat_call(messages: List[Dict[str, str]], model: str = MODEL) -> Dict[str, Any]:
    return openai_call(messages, model)["choices"][0]["message"]["content"]
