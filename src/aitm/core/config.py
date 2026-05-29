"""Configuration for AITM."""

import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class ModelProvider(Enum):
    """Supported AI model providers."""
    BEDROCK = "bedrock"
    OPENAI = "openai"
    OLLAMA = "ollama"


# Default models per provider
DEFAULT_MODELS = {
    ModelProvider.BEDROCK: "us.anthropic.claude-sonnet-4-20250514-v1:0",
    ModelProvider.OPENAI: "gpt-4o",
    ModelProvider.OLLAMA: "llama3.1",
}

# Reasoning budget mapping (tokens) for Bedrock
BEDROCK_REASONING_BUDGET = {
    0: 0,       # Off
    1: 8000,    # Low
    2: 16000,   # Medium
    3: 32000,   # High
}

# Reasoning effort mapping for OpenAI
OPENAI_REASONING_EFFORT = {
    0: None,     # Off
    1: "low",
    2: "medium",
    3: "high",
}


@dataclass
class AITMConfig:
    """Application configuration."""

    provider: ModelProvider = ModelProvider.BEDROCK
    model_id: Optional[str] = None
    reasoning_level: int = 0
    max_threats: int = 30
    temperature: float = 0.0
    aws_region: str = field(default_factory=lambda: os.environ.get("AWS_REGION", "us-east-1"))
    openai_api_key: Optional[str] = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    ollama_base_url: str = field(default_factory=lambda: os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"))

    def __post_init__(self):
        if self.reasoning_level < 0 or self.reasoning_level > 3:
            raise ValueError("Reasoning level must be 0-3")
        if self.provider == ModelProvider.OPENAI and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable required for OpenAI provider")

    def get_model_id(self) -> str:
        """Get the model ID, using default if not explicitly set."""
        return self.model_id or DEFAULT_MODELS[self.provider]

    def get_reasoning_config(self) -> dict:
        """Get provider-specific reasoning configuration."""
        if self.reasoning_level == 0:
            return {}

        if self.provider == ModelProvider.BEDROCK:
            return {
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": BEDROCK_REASONING_BUDGET[self.reasoning_level],
                }
            }
        elif self.provider == ModelProvider.OPENAI:
            effort = OPENAI_REASONING_EFFORT[self.reasoning_level]
            return {"reasoning_effort": effort} if effort else {}
        else:
            # Ollama doesn't support reasoning modes
            return {}
