from typing import Dict, Any, List
from .base_agent import BaseAgent
import json
import re
import logging

logger = logging.getLogger(__name__)

class BackcastingAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Backcasting Agent. Your task is to review and prioritize all immediate action items from the High-Impact Initiatives Agent. Your output will help decision-makers execute the most urgent and impactful tasks first while maintaining alignment with long-term goals.

🧠 Input to Analyze
All immediate action items across:
- Near-Term (0–2 years)
- Medium-Term (2–5 years) 
- Long-Term (5–10 years)

Only from high-priority strategic initiatives as defined by the High-Impact Initiatives Agent

⚙️ How to Prioritize
Each action must be ranked using three key criteria:

**Urgency** – How soon must this be completed to maintain progress?
**Impact** – How much does it advance the solution or mitigate risks?
**Feasibility** – Can it be done now, with available resources and capacity?

📤 Output Format (Structured)
```json
{
  "near_term_prioritization": [
    {
      "rank": 1,
      "title": "Action Title",
      "justification": "Provide 5-7 sentences explaining why this is ranked highest based on urgency, impact, and feasibility criteria. Begin by explaining the urgency factors - why this action must be completed soon and what happens if it's delayed. Continue by detailing the impact this action will have on advancing the solution, mitigating risks, and creating positive outcomes. Then assess the feasibility by explaining current resource availability, capability requirements, and implementation readiness. Include analysis of how this action enables or supports other strategic initiatives. Conclude by synthesizing these three criteria to demonstrate why this ranking is optimal for achieving strategic objectives while maintaining practical implementation considerations."
    },
    {
      "rank": 2,
      "title": "Action Title", 
      "justification": "Provide 5-7 sentences explaining why this is ranked second based on urgency, impact, and feasibility criteria. Begin by explaining the urgency factors - why this action must be completed soon and what happens if it's delayed. Continue by detailing the impact this action will have on advancing the solution, mitigating risks, and creating positive outcomes. Then assess the feasibility by explaining current resource availability, capability requirements, and implementation readiness. Include analysis of how this action enables or supports other strategic initiatives. Conclude by synthesizing these three criteria to demonstrate why this ranking is optimal for achieving strategic objectives while maintaining practical implementation considerations."
    }
  ],
  "medium_term_prioritization": [
    {
      "rank": 1,
      "title": "Action Title",
      "justification": "Provide 5-7 sentences explaining why this is ranked highest based on urgency, impact, and feasibility criteria. Begin by explaining the urgency factors - why this action must be completed soon and what happens if it's delayed. Continue by detailing the impact this action will have on advancing the solution, mitigating risks, and creating positive outcomes. Then assess the feasibility by explaining current resource availability, capability requirements, and implementation readiness. Include analysis of how this action enables or supports other strategic initiatives. Conclude by synthesizing these three criteria to demonstrate why this ranking is optimal for achieving strategic objectives while maintaining practical implementation considerations."
    }
  ],
  "long_term_prioritization": [
    {
      "rank": 1,
      "title": "Action Title",
      "justification": "Provide 5-7 sentences explaining why this is ranked highest based on urgency, impact, and feasibility criteria. Begin by explaining the urgency factors - why this action must be completed soon and what happens if it's delayed. Continue by detailing the impact this action will have on advancing the solution, mitigating risks, and creating positive outcomes. Then assess the feasibility by explaining current resource availability, capability requirements, and implementation readiness. Include analysis of how this action enables or supports other strategic initiatives. Conclude by synthesizing these three criteria to demonstrate why this ranking is optimal for achieving strategic objectives while maintaining practical implementation considerations."
    }
  ]
}
```

📝 Instructions
- Rank tasks from highest to lowest (1 = top priority) within each time horizon
- Each task must have a comprehensive justification of 5-7 sentences using the 3 criteria
- If tasks are dependent on others or not yet feasible, rank them lower
- Ensure justifications are thorough, analytical, and provide clear reasoning for the prioritization

✅ Guidelines
- Prioritize urgent, high-impact, feasible tasks
- Use simple, decision-oriented language
- Keep rankings time-horizon specific, do not cross-rank between near/medium/long term
- Ensure alignment with long-term goals and strategic focus
- Provide detailed, comprehensive justifications that fully explain the ranking rationale"""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        
        # Extract High-Impact Initiatives Agent output
        high_impact_data = input_data.get('high_impact', {}).get('data', {})
        execution_ready_initiatives = high_impact_data.get('execution_ready_initiatives', [])
        
        # Extract immediate action items organized by time horizon
        near_term_actions = []
        medium_term_actions = []
        long_term_actions = []
        
        for initiative in execution_ready_initiatives:
            time_horizon = initiative.get('time_horizon', '').strip()
            immediate_tasks = initiative.get('immediate_tasks', [])
            initiative_title = initiative.get('title', 'Untitled Initiative')
            
            # Add each immediate task with context
            for task in immediate_tasks:
                task_item = {
                    'task': task,
                    'initiative': initiative_title,
                    'context': {
                        'why_important': initiative.get('why_important', ''),
                        'who_it_impacts': initiative.get('who_it_impacts', ''),
                        'estimated_cost': initiative.get('estimated_cost', '')
                    }
                }
                
                if 'Near-Term' in time_horizon:
                    near_term_actions.append(task_item)
                elif 'Medium-Term' in time_horizon:
                    medium_term_actions.append(task_item)
                elif 'Long-Term' in time_horizon:
                    long_term_actions.append(task_item)
        
        # Format actions for the prompt
        def format_actions(actions, horizon_name):
            if not actions:
                return f"\n{horizon_name} Actions: None identified"
            
            text = f"\n{horizon_name} Actions:"
            for i, action in enumerate(actions, 1):
                text += f"\n{i}. {action['task']}"
                text += f"\n   From Initiative: {action['initiative']}"
                text += f"\n   Context: {action['context']['why_important'][:100]}..."
            return text
        
        near_term_text = format_actions(near_term_actions, "Near-Term (0-2 years)")
        medium_term_text = format_actions(medium_term_actions, "Medium-Term (2-5 years)")
        long_term_text = format_actions(long_term_actions, "Long-Term (5-10 years)")
        
        return f"""Original Problem Statement: {strategic_question}

High-Impact Initiatives Agent provided the following immediate action items:
{near_term_text}
{medium_term_text}
{long_term_text}

INSTRUCTIONS: 
1. Prioritize EACH immediate action item within its time horizon using the 3 criteria (Urgency, Impact, Feasibility)
2. Output in the exact JSON format specified in your system prompt
3. Rank from 1 (highest priority) to N (lowest priority) within each time horizon
4. Provide specific justifications based on the 3 criteria for each ranking

Focus on creating an actionable priority sequence that decision-makers can execute immediately."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Parse JSON from response
            prioritization_data = self._parse_prioritization_json(response)
            
            # If JSON parsing fails, try to parse structured text
            if not prioritization_data:
                prioritization_data = self._parse_prioritization_text(response)
            
            # If still no data, create fallback structure
            if not prioritization_data:
                prioritization_data = self._create_fallback_prioritization()
            
            return self.format_output(prioritization_data, response)
            
        except Exception as e:
            logger.error(f"Error in BackcastingAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def _parse_prioritization_json(self, response: str) -> Dict[str, Any]:
        """Parse JSON-formatted prioritization from LLM response"""
        try:
            # Look for JSON blocks in the response
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            json_matches = re.findall(json_pattern, response, re.DOTALL)
            
            if json_matches:
                json_str = json_matches[0]
                data = json.loads(json_str)
                
                # Validate structure
                required_keys = ['near_term_prioritization', 'medium_term_prioritization', 'long_term_prioritization']
                if all(key in data for key in required_keys):
                    return data
            
            # Try parsing entire response as JSON
            if response.strip().startswith('{'):
                return json.loads(response.strip())
                
        except json.JSONDecodeError:
            pass
        
        return None

    def _parse_prioritization_text(self, response: str) -> Dict[str, Any]:
        """Fallback method to parse structured text if JSON parsing fails"""
        prioritization = {
            'near_term_prioritization': [],
            'medium_term_prioritization': [],
            'long_term_prioritization': []
        }
        
        lines = response.split('\n')
        current_section = None
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for time horizon sections
            if 'near_term' in line.lower() or 'near-term' in line.lower():
                current_section = 'near_term_prioritization'
                continue
            elif 'medium_term' in line.lower() or 'medium-term' in line.lower():
                current_section = 'medium_term_prioritization'
                continue
            elif 'long_term' in line.lower() or 'long-term' in line.lower():
                current_section = 'long_term_prioritization'
                continue
            
            # Parse numbered items
            if current_section and re.match(r'^\d+\.', line):
                # Save previous item
                if current_item and 'title' in current_item:
                    prioritization[current_section].append(current_item)
                
                # Start new item
                rank_match = re.match(r'^(\d+)\.\s*(.+)', line)
                if rank_match:
                    current_item = {
                        'rank': int(rank_match.group(1)),
                        'title': rank_match.group(2),
                        'justification': ''
                    }
            
            # Parse justification
            elif current_item and ('justification' in line.lower() or 'reason' in line.lower()):
                justification_text = line.split(':', 1)[1].strip() if ':' in line else line
                current_item['justification'] = justification_text
            
            # Continue previous justification
            elif current_item and current_item.get('justification') and not re.match(r'^\d+\.', line):
                current_item['justification'] += ' ' + line
        
        # Save last item
        if current_item and 'title' in current_item and current_section:
            prioritization[current_section].append(current_item)
        
        return prioritization

    def _create_fallback_prioritization(self) -> Dict[str, Any]:
        """Create fallback prioritization structure"""
        return {
            'near_term_prioritization': [
                {
                    'rank': 1,
                    'title': 'Define strategic implementation framework',
                    'justification': 'High urgency to establish foundation, high impact on all subsequent actions, highly feasible with current resources'
                }
            ],
            'medium_term_prioritization': [
                {
                    'rank': 1,
                    'title': 'Execute strategic initiatives based on near-term foundations',
                    'justification': 'Medium urgency following near-term setup, high impact on strategic goals, feasible with developed capabilities'
                }
            ],
            'long_term_prioritization': [
                {
                    'rank': 1,
                    'title': 'Sustain and scale strategic outcomes',
                    'justification': 'Lower urgency but essential for sustainability, very high long-term impact, feasible with established systems'
                }
            ]
        }

    def format_output(self, prioritization_data: Dict[str, Any], response: str) -> Dict[str, Any]:
        """Format the output in a structured way."""
        # Create a human-readable markdown format
        markdown_output = "# Action Item Prioritization by Time Horizon\n\n"
        
        time_horizons = {
            'near_term_prioritization': 'Near-Term (0–2 years)',
            'medium_term_prioritization': 'Medium-Term (2–5 years)',
            'long_term_prioritization': 'Long-Term (5–10 years)'
        }
        
        for section_key, section_title in time_horizons.items():
            items = prioritization_data.get(section_key, [])
            if items:
                markdown_output += f"## {section_title}\n\n"
                for item in sorted(items, key=lambda x: x.get('rank', 999)):
                    rank = item.get('rank', 'N/A')
                    title = item.get('title', 'Untitled Action')
                    justification = item.get('justification', 'No justification provided')
                    
                    markdown_output += f"### {rank}. {title}\n\n"
                    markdown_output += f"**Justification:** {justification}\n\n"
                    markdown_output += "---\n\n"
            else:
                markdown_output += f"## {section_title}\n\nNo action items identified for this time horizon.\n\n"
        
        return {
            "status": "success",
            "data": {
                "prioritized_actions": prioritization_data,
                "formatted_output": markdown_output,
                "raw_llm_response": response
            }
        }