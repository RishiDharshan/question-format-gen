from openai import OpenAI, AsyncOpenAI
import openai
import instructor
from typing import Any, TypeVar
from pydantic import BaseModel
import time, random
from tenacity import retry, retry_if_exception_type, wait_random_exponential, stop_after_attempt

T = TypeVar('T', bound=BaseModel)

@retry(
wait=wait_random_exponential(multiplier=1, max=60),
stop=stop_after_attempt(6),
retry=retry_if_exception_type(openai.RateLimitError)
)
def generate(client: OpenAI, user_prompt: str, system_prompt: str | None = None, model: str = 'gpt-4o',response_model: T | None = None) -> T | Any:
    client = instructor.from_openai(client=client)
    if system_prompt is not None:
        messages = [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role" : "user",
                            "content": user_prompt + "\n" + f" [System Ref: {int(time.time())}-{random.randint(1,1000)}]"
                        }
        ]
    else:
        messages = [
                        {
                            "role" : "user",
                            "content": user_prompt + "\n" + f" [System Ref: {int(time.time())}-{random.randint(1,1000)}]"
                        }
        ]
    try:
        response = client.chat.completions.create(
            model=model,
            response_model=response_model,
            #reasoning_effort='medium',
            messages=messages
        )
        return response
    except Exception as e:
        print(f"The following exception occurred while trying to generate content.\nError: {e}\n")
        return str(e)
    
@retry(
wait=wait_random_exponential(multiplier=1, max=60),
stop=stop_after_attempt(6),
retry=retry_if_exception_type(openai.RateLimitError)
)
async def agenerate(client: AsyncOpenAI, user_prompt: str, system_prompt: str | None = None, model: str = 'gpt-5.2',response_model: T | None = None) -> T | Any:
    aclient = instructor.from_openai(client=client)
    if system_prompt is not None:
        messages = [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role" : "user",
                            "content": user_prompt + "\n" + f" [System Ref: {int(time.time())}-{random.randint(1,1000)}]"
                        }
        ]
    else:
        messages = [
                        {
                            "role" : "developer",
                            "content": user_prompt + "\n" + f" [System Ref: {int(time.time())}-{random.randint(1,1000)}]"
                        }
        ]
    try:
        response = await aclient.chat.completions.create(
            model=model,
            response_model=response_model,
            reasoning_effort='medium',
            messages=messages
        )
        return response
    except Exception as e:
        print(f"The following exception occurred while trying to generate content.\nError: {e}\n")
        return str(e)

