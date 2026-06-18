"""
Thin Azure OpenAI wrapper — all LLM calls go through here, so you can swap the
model in one place (``MODEL`` below). Credentials come from ``.env`` (see
``.env.example``):

    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, OPENAI_API_VERSION

* :func:`complete` — free-form text.
* :func:`parse` — structured output validated against a Pydantic model (the easy
  way to get JSON you can trust). Needs a deployment + api-version that support
  structured outputs (e.g. gpt-4o on a recent api-version).
"""
import os
from functools import lru_cache
from typing import Optional, Type, TypeVar

from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel

load_dotenv()

# The Azure *deployment* name. Change to match the one you were given.
MODEL = "gpt-4o"

T = TypeVar("T", bound=BaseModel)


@lru_cache(maxsize=1)
def get_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )


def _messages(prompt: str, system: Optional[str]) -> list:
    return [
        {"role": "system", "content": system or "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]


def complete(prompt: str, system: Optional[str] = None, max_tokens: int = 1024) -> str:
    """Send a prompt, return the model's text."""
    response = get_client().chat.completions.create(
        model=MODEL, max_tokens=max_tokens, messages=_messages(prompt, system)
    )
    return response.choices[0].message.content or ""


def parse(prompt: str, schema: Type[T], system: Optional[str] = None, max_tokens: int = 2048) -> T:
    """Send a prompt, return a validated instance of ``schema`` (structured output)."""
    response = get_client().chat.completions.parse(
        model=MODEL,
        max_tokens=max_tokens,
        messages=_messages(prompt, system),
        response_format=schema,
    )
    parsed = response.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError(f"Model did not return output matching {schema.__name__}")
    return parsed
