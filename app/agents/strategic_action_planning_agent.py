from typing import Dict, Any
from .base_agent import BaseAgent

class StrategicActionPlanningAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Strategic Action Planning Agent. Your mission is to develop actionable strategic plans based on the research synthesis. Focus on:

1. Strategic Objectives: Define clear, measurable objectives
2. Action Plans: Develop detailed action plans for each objective
3. Resource Requirements: Identify necessary resources and capabilities
4. Timeline and Milestones: Create a realistic timeline with key milestones
5. Risk Mitigation: Develop strategies to address potential risks

Your plans should be practical, achievable, and aligned with the strategic goals."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        return f"""Develop strategic action plans for the following challenge:

Strategic Question: {input_data.get('strategic_question', 'N/A')}
Time Frame: {input_data.get('time_frame', 'N/A')}
Region: {input_data.get('region', 'N/A')}
Additional Instructions: {input_data.get('prompt', 'N/A')}

Previous Analysis:
Research Synthesis: {input_data.get('research_synthesis', {}).get('data', {}).get('key_findings', [])}
Strategic Implications: {input_data.get('research_synthesis', {}).get('data', {}).get('strategic_implications', [])}

Provide a structured strategic action plan."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Parse the response into structured sections
            sections = {
                "strategic_objectives": [],
                "action_plans": [],
                "resource_requirements": [],
                "timeline_milestones": [],
                "risk_mitigation": []
            }
            
            # Basic parsing of the response
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if "Strategic Objectives" in line:
                    current_section = "strategic_objectives"
                elif "Action Plans" in line:
                    current_section = "action_plans"
                elif "Resource Requirements" in line:
                    current_section = "resource_requirements"
                elif "Timeline" in line:
                    current_section = "timeline_milestones"
                elif "Risk Mitigation" in line:
                    current_section = "risk_mitigation"
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