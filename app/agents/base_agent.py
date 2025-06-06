from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
import asyncio
from app.core.llm import get_llm
import json
import logging
import sys
from fastapi import HTTPException
import time
import random

# Configure basic logging to stdout only
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # Simplified format
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

# Disable noisy logging
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self):
        self.llm = get_llm()
        self.max_retries = 3  # Reduced retries for deployment
        self.timeout = 90  # Reduced timeout for deployment constraints
        self.base_retry_delay = 1  # Faster retry for deployment
        self.system_prompt = self.get_system_prompt()
        self.required_fields = ['strategic_question', 'time_frame', 'region']
        self.optional_fields = ['additional_context']

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the system prompt for this agent.
        Each agent must implement this method.
        """
        raise NotImplementedError("Each agent must implement get_system_prompt")

    @abstractmethod
    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        """
        Format the input data into a prompt for the LLM.
        Each agent must implement this method.
        """
        raise NotImplementedError("Each agent must implement format_prompt")

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate the input data"""
        # Check required fields
        missing_fields = [field for field in self.required_fields if field not in input_data]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )

        # Validate field types
        if not isinstance(input_data['strategic_question'], str):
            raise HTTPException(
                status_code=400,
                detail="strategic_question must be a string"
            )
        if not isinstance(input_data['time_frame'], str):
            raise HTTPException(
                status_code=400,
                detail="time_frame must be a string"
            )
        if not isinstance(input_data['region'], str):
            raise HTTPException(
                status_code=400,
                detail="region must be a string"
            )
        if 'additional_context' in input_data and not isinstance(input_data['additional_context'], str):
            raise HTTPException(
                status_code=400,
                detail="additional_context must be a string"
            )

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output data"""
        return {
            "status": "success",
            "data": data,
            "agent_type": self.__class__.__name__
        }

    def is_rate_limit_error(self, error: Exception) -> bool:
        """Check if the error is a rate limit (429) error"""
        error_str = str(error).lower()
        return (
            "429" in error_str or 
            "rate limit" in error_str or 
            "quota exceeded" in error_str or
            "service tier capacity exceeded" in error_str or
            "too many requests" in error_str
        )

    async def invoke_llm(self, prompt: str) -> str:
        """Invoke the LLM with enhanced retry logic for rate limits and timeout"""
        for attempt in range(self.max_retries):
            try:
                messages = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=prompt)
                ]
                
                response = await asyncio.wait_for(
                    self.llm.ainvoke(messages),
                    timeout=self.timeout
                )
                
                return response.content
                
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    delay = self.base_retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Timeout on attempt {attempt + 1}, retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                    continue
                raise TimeoutError(f"Agent timed out. Please try again with a more focused prompt.")
            
            except Exception as e:
                if self.is_rate_limit_error(e):
                    if attempt < self.max_retries - 1:
                        # Exponential backoff with jitter for rate limit errors
                        delay = self.base_retry_delay * (2 ** attempt) + random.uniform(0, 2)
                        logger.warning(f"Rate limit hit on attempt {attempt + 1}, retrying in {delay:.2f} seconds...")
                        await asyncio.sleep(delay)
                        continue
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please try again later."
                    )
                else:
                    if attempt < self.max_retries - 1:
                        delay = self.base_retry_delay + random.uniform(0, 1)
                        logger.warning(f"Error on attempt {attempt + 1}: {str(e)}, retrying in {delay:.2f} seconds...")
                        await asyncio.sleep(delay)
                        continue
                    raise e

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return the result"""
        try:
            # Validate input data
            self.validate_input(input_data)
            
            agent_name = self.__class__.__name__
            logger.info(f"\n{'='*80}\n{agent_name} Output:\n{'='*80}")
            
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Process the response and get output
            output = self.format_output({"response": response})
            
            # Log the final output in a clean format
            logger.info(f"\n{json.dumps(output['data'], indent=2)}\n")
            logger.info(f"{'='*80}\n")
            
            return output
            
        except HTTPException as he:
            logger.error(f"HTTP Exception: {he.detail}")
            return {
                "status": "error",
                "error": he.detail,
                "agent_type": self.__class__.__name__
            }
        except Exception as e:
            error_output = {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }
            logger.error(f"Error in {self.__class__.__name__}: {str(e)}")
            return error_output 