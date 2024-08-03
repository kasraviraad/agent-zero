
import requests

from langchain.llms import BaseLLM # type: ignore
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs.llm_result import LLMResult
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion
from typing import List, Optional, Any
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key_from_env = os.getenv("API_KEY_PERPLEXITY")

def PerplexitySearchLLM(api_key=None, model_name="sonar-medium-online", base_url="https://api.perplexity.ai"):    
    if not api_key and not api_key_from_env:
        raise ValueError("API key not provided and OPENAI_API_KEY environment variable not set.")
    
    client = OpenAI(api_key=api_key or api_key_from_env, base_url=base_url)
        
    def call_model(query: str) -> str:
        messages: List[ChatCompletionMessageParam] = [
            {
                "role": "user",
                "content": query
            }
        ]
        
        response: ChatCompletion = client.chat.completions.create(
            model=model_name,
            messages=messages,
        )
        result = response.choices[0].message.content
        return result if result is not None else ""
    
    return call_model

# Only create the call_llm function if the API key is available
if api_key_from_env:
    call_llm = PerplexitySearchLLM(model_name="llama-3-sonar-large-32k-online")
else:
    call_llm = None

def perplexity_search(search_query: str) -> str:
    if call_llm:
        return call_llm(search_query)
    else:
        return "Perplexity search is not available due to missing API key."