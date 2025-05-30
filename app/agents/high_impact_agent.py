from typing import Dict, Any, List
from .base_agent import BaseAgent

class HighImpactAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the High Impact Agent. Your mission is to identify high-impact initiatives that can drive significant value. Focus on:

1. Strategic Initiatives: List 2-3 major initiatives that can create transformative impact.
2. Quick Wins: List 2-3 immediate opportunities that can deliver value quickly.
3. Innovation Opportunities: List 2-3 innovative approaches or technologies to explore.
4. Resource Allocation: List key resources needed for these initiatives.
5. Success Metrics: List 2-3 key metrics to measure success.

Format your response exactly like this:

Strategic Initiatives:
- [Initiative 1]
- [Initiative 2]
- [Initiative 3]

Quick Wins:
- [Quick Win 1]
- [Quick Win 2]
- [Quick Win 3]

Innovation Opportunities:
- [Opportunity 1]
- [Opportunity 2]
- [Opportunity 3]

Resource Allocation:
- [Resource 1]
- [Resource 2]
- [Resource 3]

Success Metrics:
- [Metric 1]
- [Metric 2]
- [Metric 3]

Keep your initiatives focused on high-impact outcomes and measurable results."""

    def _convert_list_to_string_for_prompt(self, items: List[str]) -> str:
        if not items:
            return "N/A"
        return "\n- " + "\n- ".join(items)

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        action_plan = input_data.get('strategic_action', {}).get('data', {}).get('raw_sections', {})
        best_practices_output = input_data.get('best_practices', {}).get('data', {})
        best_practices_list = best_practices_output.get('structured_practices', [])
        
        # Format action plan sections
        short_term = action_plan.get('short_term_actions', [])
        medium_term = action_plan.get('medium_term_actions', [])
        long_term = action_plan.get('long_term_actions', [])
        
        short_term_text = "\n".join([f"- {action}" for action in short_term]) if short_term else "N/A"
        medium_term_text = "\n".join([f"- {action}" for action in medium_term]) if medium_term else "N/A"
        long_term_text = "\n".join([f"- {action}" for action in long_term]) if long_term else "N/A"
        
        # Format best practices
        best_practices_text = "\n".join([f"- {p.get('title', 'N/A')}: {p.get('description', 'N/A')}" for p in best_practices_list[:2]]) if best_practices_list else "N/A"

        return f"""Identify high-impact initiatives for: {strategic_question}

Current Action Plan:
Short-term Actions:
{short_term_text}

Medium-term Actions:
{medium_term_text}

Long-term Actions:
{long_term_text}

Relevant Best Practices:
{best_practices_text}

Additional Instructions: {input_data.get('prompt', 'N/A')}

Focus on initiatives that can create maximum impact and value."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Parse the response into sections
            sections = {
                "strategic_initiatives": [],
                "quick_wins": [],
                "innovation_opportunities": [],
                "resource_allocation": [],
                "success_metrics": []
            }
            
            current_section = None
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if "Strategic Initiatives" in line:
                    current_section = "strategic_initiatives"
                    continue
                elif "Quick Wins" in line:
                    current_section = "quick_wins"
                    continue
                elif "Innovation Opportunities" in line:
                    current_section = "innovation_opportunities"
                    continue
                elif "Resource Allocation" in line:
                    current_section = "resource_allocation"
                    continue
                elif "Success Metrics" in line:
                    current_section = "success_metrics"
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
                    sections[section] = ["No specific initiatives identified"]
            
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
        markdown_output = f"""# High-Impact Initiatives

## Strategic Initiatives
{chr(10).join(f"- {initiative}" for initiative in sections['strategic_initiatives'])}

## Quick Wins
{chr(10).join(f"- {win}" for win in sections['quick_wins'])}

## Innovation Opportunities
{chr(10).join(f"- {opportunity}" for opportunity in sections['innovation_opportunities'])}

## Resource Allocation
{chr(10).join(f"- {allocation}" for allocation in sections['resource_allocation'])}

## Success Metrics
{chr(10).join(f"- {metric}" for metric in sections['success_metrics'])}
"""

        return {
            "status": "success",
            "data": {
                "raw_sections": sections,
                "formatted_output": markdown_output
            }
        } 