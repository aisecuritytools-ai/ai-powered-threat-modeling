"""LLM provider abstraction layer.

Supports Amazon Bedrock, OpenAI, and Ollama (local).
Designed so future providers can be added without changing the engine or workflow code.
"""

from typing import List, Type
from pydantic import BaseModel
from langchain_core.messages import BaseMessage

from aitm.core.config import AITMConfig, ModelProvider


def create_llm(config: AITMConfig):
    """Create the appropriate LLM client based on config."""
    if config.provider == ModelProvider.BEDROCK:
        return _create_bedrock_llm(config)
    elif config.provider == ModelProvider.OPENAI:
        return _create_openai_llm(config)
    elif config.provider == ModelProvider.OLLAMA:
        return _create_ollama_llm(config)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")


def _create_bedrock_llm(config: AITMConfig):
    """Create Amazon Bedrock LLM."""
    from langchain_aws import ChatBedrockConverse

    kwargs = {
        "model": config.get_model_id(),
        "region_name": config.aws_region,
        "max_tokens": 8192,
    }

    reasoning_config = config.get_reasoning_config()
    if reasoning_config:
        kwargs["temperature"] = 1  # Required for reasoning models
        kwargs["model_kwargs"] = {"thinking": reasoning_config["thinking"]}
    else:
        kwargs["temperature"] = config.temperature

    return ChatBedrockConverse(**kwargs)


def _create_openai_llm(config: AITMConfig):
    """Create OpenAI LLM."""
    from langchain_openai import ChatOpenAI

    kwargs = {}
    reasoning_config = config.get_reasoning_config()
    if reasoning_config and "reasoning_effort" in reasoning_config:
        kwargs["model_kwargs"] = {"reasoning_effort": reasoning_config["reasoning_effort"]}

    return ChatOpenAI(
        model=config.get_model_id(),
        api_key=config.openai_api_key,
        temperature=config.temperature,
        max_tokens=8192,
        **kwargs,
    )


def _create_ollama_llm(config: AITMConfig):
    """Create Ollama LLM (local, free, no API key needed).

    Requires Ollama running locally: https://ollama.com
    Install: brew install ollama (macOS) or curl -fsSL https://ollama.com/install.sh | sh (Linux)
    Pull model: ollama pull llama3.1
    """
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=config.get_model_id(),
        base_url=config.ollama_base_url,
        temperature=config.temperature,
        num_predict=8192,
        format="json",  # Helps with structured output
    )


def invoke_structured(
    llm,
    messages: List[BaseMessage],
    output_schema: Type[BaseModel],
) -> BaseModel:
    """Invoke LLM with structured output parsing.

    Uses LangChain's with_structured_output for reliable JSON extraction.
    """
    structured_llm = llm.with_structured_output(output_schema)
    return structured_llm.invoke(messages)
