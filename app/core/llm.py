from langchain_mistralai.chat_models import ChatMistralAI
import os
from dotenv import load_dotenv

def get_llm():
    """Get a configured instance of the Mistral AI chat model"""
    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not found in environment variables")
    
    return ChatMistralAI(
        temperature=0.7,
        model="mistral-large-latest",
        api_key=api_key,
        timeout=100  # Increased LLM call timeout to 100 seconds
    ) 