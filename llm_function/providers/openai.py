import asyncio
from typing import Tuple

from openai import AsyncOpenAI

from llm_function.common.cache import cached, get_cache_key_based_on_all_args
from llm_function.common.exponential_backoff import with_exponential_backoff
from llm_function.common.util import exclude, json_print


class OpenAIProvider:
    def __init__(self, model, **kwargs):
        self.model = model
        self.openai = AsyncOpenAI(
                **kwargs
                # api_key="...",
                # base_url="...",
        )

    async def generate_responses(self, prompt: str, k: int, provider_config: dict) -> Tuple[str]:
        """
        Adapts the OpenAI ChatCompletion API call according to the provided provider_config.
        """
        tasks = [run_for_prompt(openai=self.openai, prompt=prompt, model=self.model, seed=seed, **provider_config) for
                 seed in range(k)]
        responses = await asyncio.gather(*tasks)
        return responses

    def sync_generate_responses(self, prompt: str, k: int, provider_config: dict) -> Tuple[str]:
        """
        Synchronous wrapper for the async generate_responses method.
        """
        return asyncio.run(self.generate_responses(prompt=prompt, k=k, provider_config=provider_config))


# @with_exponential_backoff()
# @cached("openai_embeddings")
# async def get_embedding(string, model='text-embedding-ada-002'):
#     # TODO: you can put multiples string into one request
#     response = await openai.Embedding.acreate(input=string, model=model)
#     result = response['data'][0]['embedding']
#     return result


def get_cache_key(*args, **kwargs):
    a = kwargs['prompt'][:64]
    b = kwargs['seed']
    c = get_cache_key_based_on_all_args(*args, **exclude(kwargs, 'openai'))
    return f'{a}_{b}_{c}'


@with_exponential_backoff()
@cached("openai_chat_completions", get_cache_key)
async def run_for_prompt(openai, prompt: str, length=2500, model="gpt-4", seed=0, json_mode=False, json_schema=None):
    extra_kwargs = {}
    if json_mode or json_schema:
        # FIXME: schema
        extra_kwargs['response_format'] = {"type": "json_object"}

    chat_completion = await openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=length,
            seed=seed,
            **extra_kwargs,
    )

    result = chat_completion.choices[0].message.content
    return result
