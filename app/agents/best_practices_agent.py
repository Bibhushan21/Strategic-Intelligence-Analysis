from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import json

logger = logging.getLogger(__name__)

class BestPracticesAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Best Practices Agent. Analyze and provide 3-5 key best practices for the given strategic challenge. For each practice, provide:
1. A clear title
2. A brief description
3. A real-world example
4. Key success factors

Format your response exactly like this:
Practice 1: [Title]
Description: [1-2 sentences]
Example: [Real case study]
Success Factors:
- [Factor 1]
- [Factor 2]
- [Factor 3]

Practice 2: [Title]
..."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        time_frame = input_data.get('time_frame', 'N/A')
        region = input_data.get('region', 'N/A')
        problem_statement = input_data.get('problem_analysis', {}).get('data', {}).get('problem_statement', 'N/A')
        
        return f"""Analyze best practices for the following strategic challenge:

Strategic Question: {strategic_question}
Time Frame: {time_frame}
Region/Scope: {region}
Problem Context: {problem_statement}

Provide 3-5 key best practices that have worked in similar situations or markets. Focus on practical, actionable strategies that have proven successful."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            practices = []
            current_practice = None
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Start of a new practice
                if line.startswith('**Practice') or line.startswith('Practice'):
                    if current_practice:
                        practices.append(current_practice)
                    current_practice = {
                        "title": "",
                        "description": "",
                        "example": "",
                        "success_factors": []
                    }
                    # Extract title
                    title = line.split(':', 1)[1].strip() if ':' in line else line
                    current_practice["title"] = title.replace('*', '').strip()
                    continue
                
                if not current_practice:
                    continue
                
                # Parse different sections
                if "**Description:**" in line or "Description:" in line:
                    current_practice["description"] = line.split(':', 1)[1].strip() if ':' in line else ""
                elif "**Example:**" in line or "Example:" in line:
                    current_practice["example"] = line.split(':', 1)[1].strip() if ':' in line else ""
                elif "**Success Factors:**" in line or "Success Factors:" in line:
                    continue  # Next lines will be success factors
                elif line.startswith('- ') or line.startswith('* '):
                    if current_practice["description"] and not current_practice["example"]:
                        # If we have a description but no example, this might be part of the example
                        current_practice["example"] += (" " if current_practice["example"] else "") + line[2:].strip()
                    elif current_practice["example"]:
                        # If we have an example, these are success factors
                        current_practice["success_factors"].append(line[2:].strip())
                else:
                    # Handle multi-line content
                    if not current_practice["description"]:
                        current_practice["description"] = line
                    elif not current_practice["example"]:
                        current_practice["example"] += (" " if current_practice["example"] else "") + line
                    elif current_practice["success_factors"]:
                        # Append to the last success factor if it's a continuation
                        if current_practice["success_factors"]:
                            current_practice["success_factors"][-1] += " " + line
            
            # Add the last practice
            if current_practice:
                practices.append(current_practice)
            
            # Clean up any empty fields
            for practice in practices:
                if not practice["description"]:
                    practice["description"] = "N/A"
                if not practice["example"]:
                    practice["example"] = "N/A"
                if not practice["success_factors"]:
                    practice["success_factors"] = ["N/A"]
            
            return self.format_output(practices)
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, practices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        # Create a human-readable markdown format
        markdown_output = "# Best Practices\n\n"
        
        for practice in practices:
            markdown_output += f"## {practice['title']}\n\n"
            markdown_output += f"**Description:** {practice['description']}\n\n"
            markdown_output += f"**Example:** {practice['example']}\n\n"
            markdown_output += "**Success Factors:**\n"
            markdown_output += chr(10).join(f"- {factor}" for factor in practice['success_factors'])
            markdown_output += "\n\n"

        # Create raw sections for structured data
        raw_sections = {
            "practices": practices,
            "summary": {
                "total_practices": len(practices),
                "practice_titles": [p["title"] for p in practices],
                "total_success_factors": sum(len(p["success_factors"]) for p in practices)
            }
        }

        return {
            "status": "success",
            "data": {
                "practices": practices,
                "formatted_output": markdown_output,
                "raw_sections": raw_sections
            }
        } 