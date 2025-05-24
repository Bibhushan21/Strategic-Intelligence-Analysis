from typing import Dict, Any
from .base_agent import BaseAgent

class HorizonScanningAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Horizon Scanning Agent. Your mission is to identify key emerging trends and developments relevant to the strategic challenge. Focus on:

1. Emerging Trends: Identify 2-3 key emerging trends (e.g., PESTLE).
2. Technological Developments: Highlight 1-2 significant technology changes.
3. Market Dynamics: Note 1-2 important shifts in the market.
4. Potential Disruptions: Identify 1-2 potential disruptions or wildcard events.

Keep your analysis concise and focused on the most impactful external factors."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        return f"""Scan the horizon for the following strategic challenge:

Strategic Question: {input_data.get('strategic_question', 'N/A')}
Time Frame: {input_data.get('time_frame', 'N/A')}
Region: {input_data.get('region', 'N/A')}
Scope: {', '.join(input_data.get('scope', []))}
Additional Instructions: {input_data.get('prompt', 'N/A')}

Problem Context:
- Main Problem: {input_data.get('problem_analysis', {}).get('data', {}).get('problem_statement', 'N/A')}

Provide a structured horizon scan."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            sections = {
                "emerging_trends": [],
                "technological_developments": [],
                "market_dynamics": [],
                "potential_disruptions": [] 
            }
            
            current_section_key = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if "Emerging Trends" in line:
                    current_section_key = "emerging_trends"
                    if ':' in line and line.split(':',1)[1].strip(): sections[current_section_key].append(line.split(':',1)[1].strip())
                    continue
                elif "Technological Developments" in line:
                    current_section_key = "technological_developments"
                    if ':' in line and line.split(':',1)[1].strip(): sections[current_section_key].append(line.split(':',1)[1].strip())
                    continue
                elif "Market Dynamics" in line:
                    current_section_key = "market_dynamics"
                    if ':' in line and line.split(':',1)[1].strip(): sections[current_section_key].append(line.split(':',1)[1].strip())
                    continue
                elif "Potential Disruptions" in line:
                    current_section_key = "potential_disruptions"
                    if ':' in line and line.split(':',1)[1].strip(): sections[current_section_key].append(line.split(':',1)[1].strip())
                    continue
                
                if current_section_key:
                    if line.startswith("- ") or line.startswith("* "):
                        sections[current_section_key].append(line[2:].strip())
                    elif sections[current_section_key] and isinstance(sections[current_section_key][-1], str):
                        sections[current_section_key][-1] += " " + line
                    else:
                        sections[current_section_key].append(line)
            
            for key, value in sections.items():
                if not value:
                    sections[key] = ["N/A"]
            
            return self.format_output(sections)
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        # Create a human-readable markdown format
        markdown_output = f"""# Horizon Scan

## Emerging Trends
{chr(10).join(f"- {trend}" for trend in sections['emerging_trends'])}

## Technological Developments
{chr(10).join(f"- {tech}" for tech in sections['technological_developments'])}

## Market Dynamics
{chr(10).join(f"- {dynamic}" for dynamic in sections['market_dynamics'])}

## Potential Disruptions
{chr(10).join(f"- {disruption}" for disruption in sections['potential_disruptions'])}
"""

        return {
            "status": "success",
            "data": {
                "raw_sections": sections,
                "formatted_output": markdown_output
            }
        } 