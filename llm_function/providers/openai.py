import asyncio
from typing import Tuple

import openai

from llm_function.common.cache import cached
from llm_function.common.exponential_backoff import with_exponential_backoff


class OpenAIProvider:
    async def generate_responses(self, prompt: str, k: int, provider_config: dict) -> Tuple[str]:
        """
        Adapts the OpenAI ChatCompletion API call according to the provided provider_config.
        """
        tasks = [run_for_prompt(prompt, **provider_config) for _ in range(k)]
        responses = await asyncio.gather(*tasks)
        return responses

    def sync_generate_responses(self, prompt: str, k: int, provider_config: dict) -> Tuple[str]:
        """
        Synchronous wrapper for the async generate_responses method.
        """
        return asyncio.run(self.generate_responses(prompt, k, provider_config))


@with_exponential_backoff()
@cached("openai_embeddings")
async def get_embedding(string, model='text-embedding-ada-002'):
    # TODO: you can put multiples string into one request
    response = await openai.Embedding.acreate(input=string, model=model)
    result = response['data'][0]['embedding']
    return result


@with_exponential_backoff()
@cached("openai_chat_completions")
async def run_for_prompt(prompt: str, length=2500, model="gpt-4"):
    chat_completion = await openai.ChatCompletion.acreate(model=model,
                                                          messages=[
                                                              {"role": "user", "content": prompt}],
                                                          max_tokens=length)

    result = chat_completion['choices'][0]['message']['content']
    return result

    # TODO: there's a new "json mode"!!!!
    # completion = openai.chat.completions.create(
    #         model="gpt-4-1106-preview",
    #         response_format={"type": "json_object"},
    #         messages=[
    #             {"role": "user",
    #              "content": "translate this message to vietnamese, thailand, lao, cambodia: Hello, nice to meet you, reply in json object with key is the language code"}
    #         ]
    # )
