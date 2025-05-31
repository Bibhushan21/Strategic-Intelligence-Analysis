from typing import Dict, Any
from .base_agent import BaseAgent

class HighImpactInitiativesAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the High-Impact Initiatives Agent. Your mission is to identify and prioritize high-impact initiatives that can drive significant strategic value. Focus on:

1. Initiative Identification: Identify potential high-impact initiatives
2. Impact Assessment: Evaluate the potential impact of each initiative
3. Resource Requirements: Assess the resources needed for implementation
4. Dependencies: Identify key dependencies and prerequisites
5. Implementation Strategy: Develop a strategy for successful implementation

Your analysis should help prioritize initiatives that offer the highest strategic value."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        return f"""Identify high-impact initiatives for the following challenge:

Strategic Question: {input_data.get('strategic_question', 'N/A')}
Time Frame: {input_data.get('time_frame', 'N/A')}
Region: {input_data.get('region', 'N/A')}
Additional Instructions: {input_data.get('prompt', 'N/A')}

Previous Analysis:
Strategic Action Plan: {input_data.get('strategic_action_plan', {}).get('data', {}).get('strategic_objectives', [])}
Resource Requirements: {input_data.get('strategic_action_plan', {}).get('data', {}).get('resource_requirements', [])}

Provide a structured analysis of high-impact initiatives."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Parse the response into structured sections
            sections = {
                "initiatives": [],
                "impact_assessment": [],
                "resource_requirements": [],
                "dependencies": [],
                "implementation_strategy": []
            }
            
            # Basic parsing of the response
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if "Initiative Identification" in line:
                    current_section = "initiatives"
                elif "Impact Assessment" in line:
                    current_section = "impact_assessment"
                elif "Resource Requirements" in line:
                    current_section = "resource_requirements"
                elif "Dependencies" in line:
                    current_section = "dependencies"
                elif "Implementation Strategy" in line:
                    current_section = "implementation_strategy"
                elif current_section:
                    if line.startswith("- ") or line.startswith("* "):
                        sections[current_section].append(line[2:])
                    else:
                        sections[current_section].append(line)
            
            return self.format_output(sections)
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            } 