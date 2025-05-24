from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import json

logger = logging.getLogger(__name__)

class ScenarioPlanningAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Scenario Planning Agent. Create 3-4 distinct scenarios for EV market development in Africa. For each scenario, provide:
1. A clear title
2. A narrative description
3. Key drivers
4. Main implications

Format your response exactly like this:
Scenario 1: [Title]
Narrative: [2-3 sentences describing the scenario]
Key Driver: [Main factor driving this scenario]
Main Implication: [Key business/market impact]

Scenario 2: [Title]
..."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        problem_statement = input_data.get('problem_analysis', {}).get('data', {}).get('problem_statement', 'N/A')
        
        return f"""Create distinct scenarios for EV market development in Africa (2025-2040).

Strategic Question: {strategic_question}
Problem Context: {problem_statement}

Provide 3-4 distinct scenarios that cover different possible futures."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Log the raw response for debugging
            logger.info(f"Raw LLM Response:\n{response}")
            
            # Parse the response into structured format
            scenarios = []
            current_scenario = None
            current_section = None
            
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Start of new scenario
                if line.startswith('Scenario') or (line.startswith('**Scenario') and '**' in line):
                    if current_scenario:
                        scenarios.append(current_scenario)
                    
                    # Extract title, removing markdown formatting
                    title = line.split(':', 1)[1].strip() if ':' in line else line
                    title = title.replace('**', '').strip()
                    
                    current_scenario = {
                        'title': title,
                        'narrative': '',
                        'key_driver': '',
                        'main_implication': ''
                    }
                    current_section = None
                
                # Narrative
                elif line.startswith('Narrative:'):
                    current_section = 'narrative'
                    current_scenario['narrative'] = line.split(':', 1)[1].strip()
                
                # Key Driver
                elif line.startswith('Key Driver:'):
                    current_section = 'key_driver'
                    current_scenario['key_driver'] = line.split(':', 1)[1].strip()
                
                # Main Implication
                elif line.startswith('Main Implication:'):
                    current_section = 'main_implication'
                    current_scenario['main_implication'] = line.split(':', 1)[1].strip()
                
                elif current_section and current_scenario:
                    # Append to current section if it's a continuation
                    if current_section == 'narrative':
                        current_scenario['narrative'] += ' ' + line
                    elif current_section == 'key_driver':
                        current_scenario['key_driver'] += ' ' + line
                    elif current_section == 'main_implication':
                        current_scenario['main_implication'] += ' ' + line
            
            # Add the last scenario if exists
            if current_scenario:
                scenarios.append(current_scenario)
            
            # If no structured scenarios found, create a fallback
            if not scenarios:
                scenarios = [{
                    'title': 'General Scenario',
                    'narrative': response.strip(),
                    'key_driver': 'N/A',
                    'main_implication': 'N/A'
                }]
            
            # Log the structured output for verification
            logger.info(f"Structured Output:\n{json.dumps(scenarios, indent=2)}")
            
            return self.format_output({
                "scenarios": scenarios
            })
            
        except Exception as e:
            logger.error(f"Error in ScenarioPlanningAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            } 