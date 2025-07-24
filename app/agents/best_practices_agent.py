from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class BestPracticesAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Best Practices Agent. Your task is to find and analyze 3 to 5 REAL best practices for the given challenge using verified sources.

For each best practice, provide the following information in this exact format:

### Best Practice [Number]: [Title]
**Time Frame:** [When was it implemented]\n
**Organization:** [Who implemented it]\n
**Challenge:** [Provide 2-3 sentences describing the challenge context, its complexity, and why it was significant for the organization]\n
**Problem:** [Provide 2-3 sentences explaining what they were trying to solve, the specific pain points, and the urgency behind the need for a solution]\n
**Solution:** [Provide 2-3 sentences summarizing their approach, key methodologies used, and what made their solution unique or effective]\n
**Implementation Steps:**
1. [Provide 2-3 sentences explaining this step in detail, including specific actions taken, resources involved, and key considerations]
2. [Provide 2-3 sentences explaining this step in detail, including specific actions taken, resources involved, and key considerations]
3. [Provide 2-3 sentences explaining this step in detail, including specific actions taken, resources involved, and key considerations]
**Results:** [Provide 2-3 sentences detailing key outcomes, measurable impacts, and long-term benefits achieved from the implementation]\n
**Categorical Tags:** [Tag 1], [Tag 2], [Tag 3], [Tag 4], [Tag 5]\n
**Reference:** [Real URL, research paper, case study, or official publication]

After providing all best practices, include:

### Next Practice Recommendation
[Combined recommendation that takes the best elements from the practices above]

### Key Implementation Steps
1. [Provide 2-3 sentences explaining this step comprehensively, including rationale, execution details, and success factors]
2. [Provide 2-3 sentences explaining this step comprehensively, including rationale, execution details, and success factors]
3. [Provide 2-3 sentences explaining this step comprehensively, including rationale, execution details, and success factors]

### Success Metrics
1. [Provide 2-3 sentences explaining this metric in detail, including how to measure it, why it's important, and what success looks like]
2. [Provide 2-3 sentences explaining this metric in detail, including how to measure it, why it's important, and what success looks like]
3. [Provide 2-3 sentences explaining this metric in detail, including how to measure it, why it's important, and what success looks like]

IMPORTANT: 
- Use REAL organizations, companies, governments, or institutions
- Provide ACTUAL references (URLs, research papers, case studies)
- Base information on factual, verifiable sources
- If uncertain about specific details, use realistic but clearly indicated examples
- Provide comprehensive, detailed responses with 2-3 sentences for each specified section to ensure thorough analysis and actionable insights"""

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
            
            # Extract references from the response
            references = self._extract_references(response)
            
            # Parse practices (basic implementation)
            parsed_practices_list = self._parse_practices(response)
            
            return self.format_output({
                "raw_response": response,
                "parsed_practices": parsed_practices_list,
                "references": references
            })
            
        except Exception as e:
            logger.error(f"Error in BestPracticesAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def _extract_references(self, response: str) -> list:
        """Extract references from the response"""
        import re
        references = []
        
        # Look for **Reference:** lines
        reference_pattern = r'\*\*Reference:\*\*\s*([^\n]+)'
        matches = re.findall(reference_pattern, response, re.IGNORECASE)
        
        for i, match in enumerate(matches, 1):
            references.append({
                "id": i,
                "title": f"Best Practice {i} Reference",
                "source": match.strip()
            })
        
        return references

    def _parse_practices(self, response: str) -> list:
        """Basic parsing of practices from response"""
        practices = []
        
        # Simple implementation - split by ### Best Practice
        import re
        practice_sections = re.split(r'### Best Practice \d+:', response)
        
        for i, section in enumerate(practice_sections[1:], 1):  # Skip first empty split
            lines = section.strip().split('\n')
            if lines:
                title = lines[0].strip() if lines else f"Practice {i}"
                practices.append({
                    "number": i,
                    "title": title,
                    "content": section.strip()
                })
        
        return practices

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        raw_response = data.get("raw_response", "")
        # Get the list of practices that process() would have parsed
        structured_practices_list = data.get("parsed_practices", [])
        # Get extracted references
        references = data.get("references", [])
        
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
                "references": references, # References for display
                "raw_sections": {"raw_response": raw_response}, # Keep old raw_sections structure for compatibility if needed, or deprecate
                "raw_response": raw_response, # Direct access to raw response
                "formatted_output": markdown_output
            }
        }