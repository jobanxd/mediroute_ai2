"""
Utils for LLM Calls
"""
import os
import logging

from typing import Optional, List, Dict, Any
from openai import OpenAI, AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def _build_client() -> OpenAI:
    """
    Build the appropriate OpenAI-compatible client based on environment config.
    If AZURE_OPENAI_ENDPOINT is set, use AzureOpenAI; otherwise fall back to
    a standard OpenAI client (works for local LM Studio, OpenAI, etc.).
    """
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    if azure_endpoint:
        return AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=azure_endpoint,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )

    # Local / standard OpenAI
    client_kwargs = {"api_key": os.getenv("OPENAI_API_KEY")}
    base_url = os.getenv("OPENAI_API_BASE")
    if base_url:
        client_kwargs["base_url"] = base_url

    return OpenAI(**client_kwargs)


# Build once at module load — no need to rebuild on every call
_client = _build_client()


def _get_model() -> str:
    """
    On Azure the 'model' param must match the deployment name.
    """
    return os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("OPENAI_MODEL")


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
    request_kwargs = {
        "model": _get_model(),
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
        response = _client.chat.completions.create(**request_kwargs)
        return response
    except Exception as e:
        logger.error("Error calling LLM: %s", e)
        raise
