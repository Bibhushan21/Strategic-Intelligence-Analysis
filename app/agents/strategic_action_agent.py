from typing import Dict, Any, List
from .base_agent import BaseAgent

class StrategicActionAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Strategic Action Agent. Your mission is to develop a comprehensive action plan based on the research synthesis. Focus on:

1. Short-term Actions (0-1 year): List 3-4 immediate actions that can be taken within the next year.
2. Medium-term Actions (1-3 years): List 3-4 actions for the next 1-3 years.
3. Long-term Actions (3-5 years): List 2-3 strategic actions for 3-5 years out.
4. Resource Requirements: List key resources needed (financial, human, technical).
5. Risk Mitigation: List 2-3 key risks and how to mitigate them.

Format your response exactly like this:

Short-term Actions (0-1 year):
- [Action 1]
- [Action 2]
- [Action 3]

Medium-term Actions (1-3 years):
- [Action 1]
- [Action 2]
- [Action 3]

Long-term Actions (3-5 years):
- [Action 1]
- [Action 2]

Resource Requirements:
- [Resource 1]
- [Resource 2]
- [Resource 3]

Risk Mitigation:
- [Risk 1]: [Mitigation strategy]
- [Risk 2]: [Mitigation strategy]

Keep your action plan specific, measurable, and aligned with the strategic objectives."""

    def _convert_list_to_string_for_prompt(self, items: List[str]) -> str:
        if not items:
            return "N/A"
        return "\n- " + "\n- ".join(items)

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        synthesis = input_data.get('synthesis', {}).get('data', {}).get('raw_sections', {})
        best_practices = input_data.get('best_practices', {}).get('data', {}).get('practices', [])
        
        # Format synthesis insights
        insights = synthesis.get('key_insights', [])
        implications = synthesis.get('strategic_implications', [])
        recommendations = synthesis.get('recommendations', [])
        
        insights_text = "\n".join([f"- {insight}" for insight in insights]) if insights else "N/A"
        implications_text = "\n".join([f"- {implication}" for implication in implications]) if implications else "N/A"
        recommendations_text = "\n".join([f"- {recommendation}" for recommendation in recommendations]) if recommendations else "N/A"
        
        # Format best practices
        best_practices_text = "\n".join([f"- {p['title']}: {p['description']}" for p in best_practices[:2]]) if best_practices else "N/A"

        return f"""Develop a strategic action plan for: {strategic_question}

Key Insights from Research:
{insights_text}

Strategic Implications:
{implications_text}

Key Recommendations:
{recommendations_text}

Relevant Best Practices:
{best_practices_text}

Additional Instructions: {input_data.get('prompt', 'N/A')}

Create a detailed action plan that addresses these insights and recommendations."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Parse the response into sections
            sections = {
                "short_term_actions": [],
                "medium_term_actions": [],
                "long_term_actions": [],
                "resource_requirements": [],
                "risk_mitigation": []
            }
            
            current_section = None
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if "Short-term Actions" in line:
                    current_section = "short_term_actions"
                    continue
                elif "Medium-term Actions" in line:
                    current_section = "medium_term_actions"
                    continue
                elif "Long-term Actions" in line:
                    current_section = "long_term_actions"
                    continue
                elif "Resource Requirements" in line:
                    current_section = "resource_requirements"
                    continue
                elif "Risk Mitigation" in line:
                    current_section = "risk_mitigation"
                    continue
                
                # Add content to current section
                if current_section and (line.startswith('- ') or line.startswith('* ')):
                    sections[current_section].append(line[2:].strip())
                elif current_section:
                    # Handle multi-line content
                    if sections[current_section]:
                        sections[current_section][-1] += " " + line
                    else:
                        sections[current_section].append(line)
            
            # Ensure no empty sections
            for section in sections:
                if not sections[section]:
                    sections[section] = ["No specific actions identified"]
            
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
        markdown_output = f"""# Strategic Action Plan

## Short-term Actions (0-1 year)
{chr(10).join(f"- {action}" for action in sections['short_term_actions'])}

## Medium-term Actions (1-3 years)
{chr(10).join(f"- {action}" for action in sections['medium_term_actions'])}

## Long-term Actions (3-5 years)
{chr(10).join(f"- {action}" for action in sections['long_term_actions'])}

## Resource Requirements
{chr(10).join(f"- {resource}" for resource in sections['resource_requirements'])}

## Risk Mitigation
{chr(10).join(f"- {risk}" for risk in sections['risk_mitigation'])}
"""

        return {
            "status": "success",
            "data": {
                "raw_sections": sections,
                "formatted_output": markdown_output
            }
        } 