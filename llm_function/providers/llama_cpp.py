import asyncio

from llama_cpp import Llama

from llm_function.common.cache import cached, get_cache_key_based_on_all_args
from llm_function.common.util import exclude


class LlamaCppProvider:
    def __init__(self, model_path, n_ctx=1024, verbose=False, **extra_args):
        # FIXME: needed?
        # self.model_path = model_path
        # self.verbose = verbose
        # self.n_ctx = n_ctx

        self.llm = Llama(
                n_gpu_layers=-1,
                chat_format="chatml",
                n_ctx=n_ctx,
                model_path=model_path,
                verbose=verbose,
                **extra_args
        )

    async def generate_responses(self, prompt: str, k: int, provider_config: dict) -> tuple[str]:
        """
        Adapts the OpenAI ChatCompletion API call according to the provided provider_config.
        """

        responses = []
        for seed in range(k):
            r = await run_for_prompt(llm=self.llm,
                                     prompt=prompt,
                                     seed=seed,
                                     **provider_config)
            responses.append(r)

        return responses

    def sync_generate_responses(self, prompt: str, k: int, provider_config: dict) -> tuple[str]:
        """
        Synchronous wrapper for the async generate_responses method.
        """
        return asyncio.run(self.generate_responses(prompt, k, provider_config))


def get_cache_key(*args, **kwargs):
    a = kwargs['prompt'][:64]
    b = kwargs['seed']
    c = get_cache_key_based_on_all_args(*args, **exclude(kwargs, 'llm'))
    return f'{a}_{b}_{c}'


@cached("llama_cpp_chat_completions", get_cache_key)
async def run_for_prompt(llm,
                         prompt: str,
                         system_prompt: str = 'You are a helpful AI assistant.',
                         json_schema: dict = None,
                         length: int = 2000,
                         seed: int = 1337,  # Uncomment to set a specific seed
                         temperature: float = 0.7,
                         # n_ctx=128*1024, # Uncomment to increase the context window
                         **extra_params):
    extra_completion_kwargs = {}
    if json_schema:
        extra_completion_kwargs['response_format'] = {
            "type": "json_object",
            "schema": json_schema
        }

    response = llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=length,
            seed=seed,
            # TODO: test
            # stop=["\n\n"],
            **extra_completion_kwargs
    )

    return response['choices'][0]['message']['content']
