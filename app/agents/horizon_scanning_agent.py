from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import asyncio

logger = logging.getLogger(__name__)

class HorizonScanningAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Strategic Horizon Scanning Agent. Identify up to 3 critical Weak Signals and up to 3 Key Uncertainties.

Format your response exactly like this:

## Weak Signals:
**[Number]. [Title]**\n
   - **Domain:** [Domain]
    **Description:** [2 sentence]
    **Impact:** [1-10]
    **Time:** [Near/Medium/Long]\n

##Key Uncertainties:
** [Number]. [Title]**\n
   - **Domain:** [Domain]
    **Description:** [2 sentence]
    **Impact:** [1-10]
    **Time:** [Near/Medium/Long]\n

## Change Drivers:

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
        
        problem_explorer_data = input_data.get('problem_explorer', {}).get('data', {}).get('structured_output', {})
        problem_summary = "Not available."
        if problem_explorer_data:
            # Try to get a concise problem definition from Phase 1 or acknowledgment
            phase1_content_list = problem_explorer_data.get('phase1', {}).get('content', [])
            if isinstance(phase1_content_list, list) and phase1_content_list:
                # Take the first item of phase1 content, split into words, take first 30, rejoin.
                first_item_words = str(phase1_content_list[0]).split()
                problem_summary = " ".join(first_item_words[:30])
                if len(first_item_words) > 30:
                    problem_summary += "..."
            elif problem_explorer_data.get('acknowledgment'):
                 problem_summary = str(problem_explorer_data.get('acknowledgment', '')).strip()
                 if len(problem_summary.split()) > 40: # Keep acknowledgment summary brief too
                     ack_words = problem_summary.split()
                     problem_summary = " ".join(ack_words[:40]) + "..."
            if not problem_summary.strip() or problem_summary == "Not available.": # Fallback if phase1 and ack are empty
                problem_summary = "General context based on strategic question."

        return f"""Given the strategic question: \"{strategic_question}\"
And the core problem context: \"{problem_summary}\"
For the time frame \"{time_frame}\" and region \"{region}\":

Identify up to 3 critical Weak Signals, up to 3 Key Uncertainties, and the main Change Drivers (one for each relevant STEEPLED category).
Focus on the most impactful and relevant items for the problem context.
For each Weak Signal and Key Uncertainty, provide a title, domain, a 1-2 sentence description, impact rating, and time frame.
Adhere strictly to the output format sections: ## Weak Signals:, ## Key Uncertainties:, ## Change Drivers: as specified in system instructions."""

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