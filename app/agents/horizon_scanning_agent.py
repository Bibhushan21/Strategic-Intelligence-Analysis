from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import asyncio

logger = logging.getLogger(__name__)

class HorizonScanningAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Strategic Horizon Scanning Agent. Identify the top 5 most critical trends and uncertainties.

Format your response exactly like this:

## Weak Signals:
**[Number]. [Title]**\n
   - **Domain:** [Domain]
    **Description:** [3 sentence]
    **Impact:** [1-10]
    **Time:** [Near/Medium/Long]\n


\n##Key Uncertainties:
** [Number]. [Title]**\n
   - **Domain:** [Domain]
    **Description:** [3 sentence]
    **Impact:** [1-10]
    **Time:** [Near/Medium/Long]\n


## Change Drivers:\n
**Tech:** [1 key driver]\n
**Market:** [1 key driver]\n
**Society:** [1 key driver]\n
**Demographics:** [1 key driver]\n
**Economic:** [1 key driver]\n
**Political:** [1 key driver]\n
**Legal:** [1 key driver]\n
**Environmental:** [1 key driver]\n
"""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        time_frame = input_data.get('time_frame', 'N/A')
        region = input_data.get('region', 'N/A')
        
        return f"""Analyze: {strategic_question}
Time: {time_frame}
Region: {region}

Keep responses extremely brief and focused."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await asyncio.wait_for(
                self.invoke_llm(prompt),
                timeout=15
            )
            
            # Log the raw response for debugging
            logger.info(f"Raw LLM Response:\n{response}")
            
            return self.format_output({
                "raw_response": response
            })
            
        except asyncio.TimeoutError:
            logger.error("HorizonScanningAgent timed out")
            return {
                "status": "error",
                "error": "Agent timed out. Please try again with a more focused prompt.",
                "agent_type": self.__class__.__name__
            }
        except Exception as e:
            logger.error(f"Error in HorizonScanningAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        raw_response = data.get("raw_response", "")
        
        # Create a human-readable markdown format that matches the raw output
        markdown_output = "# Horizon Scanning Analysis\n\n"
        
        # Split the raw response into sections
        sections = raw_response.split("\n\n")
        
        for section in sections:
            if section.strip():
                # Add each section as is, preserving the original format
                markdown_output += f"{section}\n\n"
                
                # Add a separator between signals and uncertainties for better readability
                if ("**Weak Signals:**" in section or "**Key Uncertainties:**" in section) and "**Change Drivers:**" not in section:
                    markdown_output += "---\n\n"
        
        return {
            "status": "success",
            "data": {
                "raw_sections": data,
                "formatted_output": markdown_output
            }
        }