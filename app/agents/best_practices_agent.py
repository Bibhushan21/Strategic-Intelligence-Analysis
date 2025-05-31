from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class BestPracticesAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Best Practices Agent. Your task is to find and analyze 3 to 5 best practices for the given challenge.

For each best practice, provide the following information in this exact format:

### Best Practice [Number]: [Title]
**Time Frame:** [When was it implemented]\n
**Organization:** [Who implemented it]\n
**Challenge:** [What was the challenge context]\n
**Problem:** [What they were trying to solve]\n
**Solution:** [Brief summary of their approach]\n
**Implementation Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]
**Results:** [Key outcomes or impact]\n
**Categorical Tags:** [Tag 1], [Tag 2], [Tag 3], [Tag 4], [Tag 5]\n
**Source:** [Where this information comes from]

After providing all best practices, include:

### Next Practice Recommendation
[Combined recommendation that takes the best elements from the practices above]

### Key Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Success Metrics
1. [Metric 1]
2. [Metric 2]
3. [Metric 3]

Keep responses concise and focused on actionable insights. Ensure all sections and fields are included for each best practice."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        time_frame = input_data.get('time_frame', 'N/A')
        region = input_data.get('region', 'N/A')
        # Get the structured output from ProblemExplorerAgent
        problem_explorer_output = input_data.get('problem_explorer', {}).get('data', {}).get('structured_output', {})
        
        problem_context = ""
        if problem_explorer_output:
            # Extract content from Phase 1: Define the Problem
            phase1_content = problem_explorer_output.get('phase1', {}).get('content', [])
            if phase1_content:
                problem_context += "\n".join(phase1_content)
            
            # Optionally, add acknowledgment or other relevant parts
            acknowledgment = problem_explorer_output.get('acknowledgment', '')
            if acknowledgment:
                problem_context = f"{acknowledgment}\n{problem_context}" # Prepend acknowledgment
        
        return f"""Strategic Question: {strategic_question}
Time Frame: {time_frame}
Region/Scope: {region}

Problem Context:
{problem_context if problem_context else 'Problem context not available from Problem Explorer.'}

Please provide 3 best practices and a next practice recommendation."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Log the raw response for debugging
            logger.info(f"Raw LLM Response:\n{response}")
            
            # TODO: Implement parsing of 'response' into a list of structured practice dictionaries
            parsed_practices_list = [] 
            
            return self.format_output({
                "raw_response": response,
                "parsed_practices": parsed_practices_list # Pass potentially parsed data
            })
            
        except Exception as e:
            logger.error(f"Error in BestPracticesAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        raw_response = data.get("raw_response", "")
        # Get the list of practices that process() would have parsed (currently a placeholder)
        structured_practices_list = data.get("parsed_practices", [])
        
        # Create a human-readable markdown format that matches the raw output
        markdown_output = "# Best Practices Analysis\n\n"
        
        # Split the raw response into sections
        sections = raw_response.split("\n\n")
        
        for section in sections:
            if section.strip():
                # Add each section as is, preserving the original format
                markdown_output += f"{section}\n\n"
                
                # Add a separator between best practices for better readability
                if "### Best Practice" in section and "### Next Practice" not in section:
                    markdown_output += "---\n\n"
        
        return {
            "status": "success",
            "data": {
                "structured_practices": structured_practices_list, # Key for downstream
                "raw_sections": {"raw_response": raw_response}, # Keep old raw_sections structure for compatibility if needed, or deprecate
                "raw_response": raw_response, # Direct access to raw response
                "formatted_output": markdown_output
            }
        }