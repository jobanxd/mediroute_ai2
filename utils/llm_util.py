"""
Utils for LLM Calls
"""
import os
import logging

from typing import Optional, List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


async def get_llm() -> OpenAI:
    """
    Get an instance of the OpenAI client.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE")

    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    return OpenAI(**client_kwargs)


async def call_llm(
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[str | Dict[str, Any]] = None,
    response_format: Optional[Dict[str, Any]] = None,
    temperature: float = 0.3,
):
    """
    Generic LLM caller that accepts fully constructed messages
    and optional tool definitions.
    """
    client = await get_llm()
    model = os.getenv("OPENAI_MODEL")

    request_kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if tools:
        request_kwargs["tools"] = tools

    if tool_choice:
        request_kwargs["tool_choice"] = tool_choice

    if response_format:
        request_kwargs["response_format"] = response_format

    try:
        response = client.chat.completions.create(**request_kwargs)
        return response
    except Exception as e:
        logger.error("Error calling LLM: %s", e)
        raise
