from typing import Protocol, Tuple, Any
from llm_function.providers.mistral import MistralProvider
from llm_function.providers.openai import OpenAIProvider


class Provider(Protocol):
    async def generate_responses(self, prompt: str, k: int, provider_config: dict) -> Tuple[Any]:
        """Generates responses asynchronously based on the given prompt and provider configuration."""
        ...

    def sync_generate_responses(self, prompt: str, k: int, provider_config: dict) -> Tuple[Any]:
        """Synchronous wrapper for generating responses."""
        ...
