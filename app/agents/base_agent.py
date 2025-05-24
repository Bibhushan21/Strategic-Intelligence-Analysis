from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
import asyncio
from app.core.llm import get_llm
import json
import logging
import sys

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
        self.max_retries = 3
        self.timeout = 15
        self.retry_delay = 1
        self.system_prompt = self.get_system_prompt()

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

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output data"""
        return {
            "status": "success",
            "data": data,
            "agent_type": self.__class__.__name__
        }

    async def invoke_llm(self, prompt: str) -> str:
        """Invoke the LLM with retry logic and timeout"""
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
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise TimeoutError(f"Agent {self.__class__.__name__} timed out after {self.max_retries} retries")
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise e

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return the result"""
        try:
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
            
        except Exception as e:
            error_output = {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }
            logger.error(f"Error in {self.__class__.__name__}: {str(e)}")
            return error_output 