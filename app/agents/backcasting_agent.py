from typing import Dict, Any, List
from .base_agent import BaseAgent

class BackcastingAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Backcasting Agent. Your mission is to work backwards from the desired future state to identify critical path tasks and milestones. Focus on:

1. Critical Path Tasks: List 3-4 essential tasks that must be completed in sequence.
2. Milestones: List 2-3 key milestones that mark significant progress.
3. Dependencies: List 2-3 critical dependencies between tasks.
4. Timeline: List 2-3 major timeline points or deadlines.
5. Resource Requirements: List key resources needed for implementation.

Format your response exactly like this:

Critical Path Tasks:
- [Task 1]
- [Task 2]
- [Task 3]
- [Task 4]

Milestones:
- [Milestone 1]
- [Milestone 2]
- [Milestone 3]

Dependencies:
- [Dependency 1]
- [Dependency 2]
- [Dependency 3]

Timeline:
- [Timeline point 1]
- [Timeline point 2]
- [Timeline point 3]

Resource Requirements:
- [Resource 1]
- [Resource 2]
- [Resource 3]

Keep your backcasting plan focused on critical path and dependencies."""

    def _convert_list_to_string_for_prompt(self, items: List[str], prefix="- ") -> str:
        if not items:
            return "N/A"
        return "\n" + prefix + ("\n" + prefix).join(items)

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        initiatives = input_data.get('initiatives', {}).get('data', {}).get('raw_sections', {})
        action_plan = input_data.get('action_plan', {}).get('data', {}).get('raw_sections', {})
        
        # Format initiatives
        strategic = initiatives.get('strategic_initiatives', [])
        quick_wins = initiatives.get('quick_wins', [])
        innovation = initiatives.get('innovation_opportunities', [])
        
        strategic_text = "\n".join([f"- {initiative}" for initiative in strategic]) if strategic else "N/A"
        quick_wins_text = "\n".join([f"- {win}" for win in quick_wins]) if quick_wins else "N/A"
        innovation_text = "\n".join([f"- {opp}" for opp in innovation]) if innovation else "N/A"
        
        # Format action plan
        short_term = action_plan.get('short_term_actions', [])
        medium_term = action_plan.get('medium_term_actions', [])
        long_term = action_plan.get('long_term_actions', [])
        
        short_term_text = "\n".join([f"- {action}" for action in short_term]) if short_term else "N/A"
        medium_term_text = "\n".join([f"- {action}" for action in medium_term]) if medium_term else "N/A"
        long_term_text = "\n".join([f"- {action}" for action in long_term]) if long_term else "N/A"

        return f"""Develop a backcasting plan for: {strategic_question}

Strategic Initiatives:
{strategic_text}

Quick Wins:
{quick_wins_text}

Innovation Opportunities:
{innovation_text}

Current Action Plan:
Short-term Actions:
{short_term_text}

Medium-term Actions:
{medium_term_text}

Long-term Actions:
{long_term_text}

Additional Instructions: {input_data.get('prompt', 'N/A')}

Create a detailed backcasting plan that identifies critical path and dependencies."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Parse the response into sections
            sections = {
                "critical_path_tasks": [],
                "milestones": [],
                "dependencies": [],
                "timeline": [],
                "resource_requirements": []
            }
            
            current_section = None
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if "Critical Path Tasks" in line:
                    current_section = "critical_path_tasks"
                    continue
                elif "Milestones" in line:
                    current_section = "milestones"
                    continue
                elif "Dependencies" in line:
                    current_section = "dependencies"
                    continue
                elif "Timeline" in line:
                    current_section = "timeline"
                    continue
                elif "Resource Requirements" in line:
                    current_section = "resource_requirements"
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
                    sections[section] = ["No specific tasks identified"]
            
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
        markdown_output = f"""# Backcasting Analysis

## Critical Path Tasks
{chr(10).join(f"- {task}" for task in sections['critical_path_tasks'])}

## Milestones
{chr(10).join(f"- {milestone}" for milestone in sections['milestones'])}

## Dependencies
{chr(10).join(f"- {dependency}" for dependency in sections['dependencies'])}

## Timeline
{chr(10).join(f"- {timeline}" for timeline in sections['timeline'])}

## Resource Requirements
{chr(10).join(f"- {resource}" for resource in sections['resource_requirements'])}
"""

        return {
            "status": "success",
            "data": {
                "raw_sections": sections,
                "formatted_output": markdown_output
            }
        } 