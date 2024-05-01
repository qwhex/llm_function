import asyncio
from typing import Tuple

from mistralai.async_client import MistralAsyncClient
from mistralai.models.chat_completion import ChatMessage

from llm_function.common.cache import cached
from llm_function.common.config import get_config_value
from llm_function.common.exponential_backoff import with_exponential_backoff


class MistralProvider:
    async def generate_responses(self, prompt: str, k: int, provider_config) -> Tuple[str]:
        """
        Adapts the OpenAI ChatCompletion API call according to the provided provider_config.
        """
        tasks = [run_for_prompt(prompt, random_seed=i, **provider_config) for i in range(k)]
        responses = await asyncio.gather(*tasks)
        return responses

    def sync_generate_responses(self, prompt: str, k: int, provider_config) -> Tuple[str]:
        """
        Synchronous wrapper for the async generate_responses method.
        """
        return asyncio.run(self.generate_responses(prompt, k, provider_config))


# response_format={"type": "json_object"},


@with_exponential_backoff()
@cached("mistral_chat_completions")
async def run_for_prompt(prompt: str, length: int = 2000, model: str = 'mistral-large-latest', **extra_params):
    """
    messages: List[Any],
    model: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    random_seed: Optional[int] = None,
    safe_mode: bool = False,
    safe_prompt: bool = False,
    tool_choice: Optional[Union[str, ToolChoice]] = None,

    We allow users to provide a custom system prompt (see API reference).
    We also allow a convenient safe_prompt flag to force chat completion to be moderated against sensitive content
      (see Guardrailing).
    """
    client = MistralAsyncClient(api_key=get_config_value('MISTRAL_API_KEY'))

    messages = [
        ChatMessage(role='user', content=prompt)
    ]

    response = await client.chat(
            model=model,
            max_tokens=length,
            messages=messages,
            safe_prompt=False,
            **extra_params,
    )

    # print(json.dumps(response, indent=2))
    return response.choices[0].message.content
