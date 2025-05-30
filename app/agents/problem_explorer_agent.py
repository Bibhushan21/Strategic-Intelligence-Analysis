from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ProblemExplorerAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Problem Explorer Agent, a strategic analysis specialist. Your job is to break down the problem provided by the user using a clear 5-phase framework. Keep your answers short, focused, and practical. Prioritize clarity over depth to avoid overload.

Start:
Step 1: Acknowledge the problem statement and confirm your understanding in 1–2 sentences.

Phase 1: Define the Problem
What is the main problem we're solving?
Why does this matter to the stakeholders?
Who are the key people or groups affected?
What is clearly not part of the problem?
What's the current situation?

Phase 2: Break it Down
What are the key parts of this problem?
How are these parts connected?
Are there any hidden causes or unseen factors?
What similar problems could offer ideas?

Phase 3: Assess the Information
What info do we already have?
What's missing?
What would help us understand better?
How could we gather the missing info?

Phase 4: Explore Solutions
Should we go big or start small?
What ideas are worth exploring?
Have others solved similar problems?
What would a great solution look like?
What results are we aiming for?

Phase 5: Plan to Act
What are the key next steps?
Who needs to be involved?
What's a realistic timeline?
What do we need (people, money, tools)?
How will we know it's working?

✅ Finish:
List 3–5 key strategic takeaways or things to keep in mind moving forward."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        time_frame = input_data.get('time_frame', 'N/A')
        region = input_data.get('region', 'N/A')
        prompt = input_data.get('prompt', '')
        
        return f"""Strategic Question: {strategic_question}
Time Frame: {time_frame}
Region/Scope: {region}
Additional Context: {prompt if prompt else 'None provided'}

Please analyze this strategic challenge using the 5-phase framework."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Log the raw response for debugging
            logger.info(f"Raw LLM Response:\n{response}")
            
            # Parse the response into structured format
            sections = {
                'acknowledgment': '',
                'phase1': {'title': 'Define the Problem', 'content': []},
                'phase2': {'title': 'Break it Down', 'content': []},
                'phase3': {'title': 'Assess the Information', 'content': []},
                'phase4': {'title': 'Explore Solutions', 'content': []},
                'phase5': {'title': 'Plan to Act', 'content': []},
                'takeaways': []
            }
            
            current_section = None
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for acknowledgment
                if line.startswith('Step 1:') or line.startswith('I understand'):
                    sections['acknowledgment'] = line
                    continue
                
                # Check for phase headers
                if 'Phase 1:' in line:
                    current_section = 'phase1'
                    continue
                elif 'Phase 2:' in line:
                    current_section = 'phase2'
                    continue
                elif 'Phase 3:' in line or '📊' in line:
                    current_section = 'phase3'
                    continue
                elif 'Phase 4:' in line or '💡' in line:
                    current_section = 'phase4'
                    continue
                elif 'Phase 5:' in line or '🚀' in line:
                    current_section = 'phase5'
                    continue
                elif 'Finish:' in line or '✅' in line:
                    current_section = 'takeaways'
                    continue
                
                # Add content to current section
                if current_section and current_section != 'acknowledgment':
                    if current_section == 'takeaways':
                        if line.startswith('-') or line.startswith('•'):
                            sections[current_section].append(line.lstrip('- ').lstrip('• '))
                    else:
                        # Only add bullet point if the line doesn't already have one
                        if line.startswith('-') or line.startswith('•'):
                            sections[current_section]['content'].append(line)
                        else:
                            sections[current_section]['content'].append(f"- {line}")
            
            # Log the structured output
            logger.info(f"Structured Output:\n{sections}")
            
            return self.format_output({
                "raw_response": response,
                "structured_data": sections
            })
            
        except Exception as e:
            logger.error(f"Error in ProblemExplorerAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        structured_data_from_process = data.get("structured_data", {})
        raw_response_from_process = data.get("raw_response", "")
        
        # Create a human-readable markdown format
        markdown_output = "# Problem Exploration Analysis\n\n"
        
        # Add acknowledgment
        if structured_data_from_process.get('acknowledgment'):
            markdown_output += f"## Understanding\n{structured_data_from_process['acknowledgment']}\n\n"
        
        # Add each phase
        for phase in ['phase1', 'phase2', 'phase3', 'phase4', 'phase5']:
            if phase in structured_data_from_process:
                phase_data = structured_data_from_process[phase]
                markdown_output += f"## {phase_data['title']}\n\n"
                for item in phase_data['content']:
                    # Don't add bullet point if item already has one
                    if item.startswith('-') or item.startswith('•'):
                        markdown_output += f"{item}\n"
                    else:
                        markdown_output += f"- {item}\n"
                markdown_output += "\n"
        
        # Add takeaways
        if structured_data_from_process.get('takeaways'):
            markdown_output += "## Key Takeaways\n\n"
            for takeaway in structured_data_from_process['takeaways']:
                markdown_output += f"- {takeaway}\n"
        
        return {
            "status": "success",
            "data": {
                "structured_output": structured_data_from_process,
                "raw_response": raw_response_from_process,
                "formatted_output": markdown_output
            }
        } 