from langchain_mistralai.chat_models import ChatMistralAI
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import time

class RateLimitError(Exception):
    """Custom exception for rate limit errors"""
    pass

def get_llm():
    """Get a configured instance of the Mistral AI chat model"""
    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not found in environment variables")
    
    return ChatMistralAI(
        temperature=0.7,
        model="mistral-medium-latest",
        api_key=api_key,
        timeout=120,  # Increased timeout to 120 seconds
        max_retries=5,  # Enable built-in retry mechanism
    ) 