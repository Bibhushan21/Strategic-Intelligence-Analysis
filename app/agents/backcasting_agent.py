from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class BackcastingAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Backcasting Agent, focused on turning long-term strategy into action by ranking tasks across time horizons for smart execution.

🧠 Your Task:
Review the immediate action items from the High-Impact Initiatives Agent and rank them within each time horizon:

Near-Term (0–2 years)
Medium-Term (2–5 years)
Long-Term (5–10 years)

🔍 Ranking Criteria (Ask yourself for each task):
Urgency – Does this need to happen now to avoid delay?
Impact – Will this drive big results or unlock future steps?
Feasibility – Can we realistically do this now?

📊 How to Prioritize:
Assign numbers (1 = highest priority) within each time horizon.
Tasks that are urgent, impactful, and doable go to the top.
Tasks that are dependent, lower impact, or less urgent go lower.

📋 Output Format:
[Time Horizon] Immediate Task Prioritization
1. [Task Title]
Justification: [1–2 sentence reason based on urgency, impact, feasibility]
2. [Task Title]
Justification: [...]
3. [Task Title]
Justification: [...]
...
N. [Task Title]
Justification: [...]"""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        high_impact = input_data.get('high_impact', {}).get('data', {}).get('raw_sections', {})
        
        # Format high impact initiatives
        initiatives = high_impact.get('strategic_initiatives', [])
        quick_wins = high_impact.get('quick_wins', [])
        innovation = high_impact.get('innovation_opportunities', [])
        
        initiatives_text = "\n".join([f"- {initiative}" for initiative in initiatives]) if initiatives else "N/A"
        quick_wins_text = "\n".join([f"- {win}" for win in quick_wins]) if quick_wins else "N/A"
        innovation_text = "\n".join([f"- {opp}" for opp in innovation]) if innovation else "N/A"

        return f"""Strategic Question: {strategic_question}

High-Impact Initiatives:
{initiatives_text}

Quick Wins:
{quick_wins_text}

Innovation Opportunities:
{innovation_text}

Please prioritize these initiatives across time horizons."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Log the raw response for debugging
            logger.info(f"Raw LLM Response:\n{response}")
            
            # Parse the response into structured format
            sections = {
                'near_term': [],
                'medium_term': [],
                'long_term': []
            }
            
            current_section = None
            current_task = None
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for time horizon sections
                if 'Near-Term' in line:
                    current_section = 'near_term'
                    continue
                elif 'Medium-Term' in line:
                    current_section = 'medium_term'
                    continue
                elif 'Long-Term' in line:
                    current_section = 'long_term'
                    continue
                
                # Process tasks and justifications
                if current_section:
                    if line[0].isdigit() and '. ' in line:
                        if current_task:
                            sections[current_section].append(current_task)
                        current_task = {
                            'title': line.split('. ', 1)[1],
                            'justification': ''
                        }
                    elif current_task and line.startswith('Justification:'):
                        current_task['justification'] = line.split('Justification:', 1)[1].strip()
            
            # Add the last task if exists
            if current_task and current_section:
                sections[current_section].append(current_task)
            
            # Log the structured output
            logger.info(f"Structured Output:\n{sections}")
            
            return self.format_output({
                "raw_response": response,
                "structured_data": sections
            })
            
        except Exception as e:
            logger.error(f"Error in BackcastingAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        sections = data.get("structured_data", {})
        
        # Create a human-readable markdown format
        markdown_output = "# Backcasting Analysis\n\n"
        
        # Add each time horizon section
        time_horizons = {
            'near_term': 'Near-Term (0–2 years)',
            'medium_term': 'Medium-Term (2–5 years)',
            'long_term': 'Long-Term (5–10 years)'
        }
        
        for section_key, section_title in time_horizons.items():
            if section_key in sections and sections[section_key]:
                markdown_output += f"## {section_title}\n\n"
                for i, task in enumerate(sections[section_key], 1):
                    markdown_output += f"### {i}. {task['title']}\n\n"
                    markdown_output += f"**Justification:** {task['justification']}\n\n"
        
        return {
            "status": "success",
            "data": {
                "raw_sections": data,
                "formatted_output": markdown_output
            }
        }