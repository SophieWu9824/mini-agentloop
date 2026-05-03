import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")

API_KEY = os.environ.get("AGENTLOOP_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = os.environ.get("AGENTLOOP_API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("AGENTLOOP_API_MODEL", "gpt-4o")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def call_model(messages, tools=None):
    kwargs = {
        "model": MODEL_NAME,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message
