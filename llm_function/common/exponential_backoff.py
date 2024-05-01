import asyncio
import functools


def with_exponential_backoff(initial_delay=5, max_retries=5):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            retries = 0

            while retries <= max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    print(e)
                    if retries == max_retries:
                        raise
                    print(f"Error encountered. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    delay *= 2
                    retries += 1

        return wrapper

    return decorator
