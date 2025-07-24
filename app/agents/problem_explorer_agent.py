from typing import Dict, Any
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ProblemExplorerAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Problem Explorer Agent, a strategic analysis specialist. Your job is to break down the problem provided by the user using a clear 5-phase framework. Provide detailed, comprehensive responses with 2-4 sentences for each question to ensure thorough analysis while maintaining clarity and practical focus.

Start:
Step 1: Acknowledge the problem statement and confirm your understanding in 1–2 sentences.

Phase 1: Define the Problem
What is the main problem we're solving? (Provide 2-4 sentences explaining the core issue, its scope, and primary characteristics)
Why does this matter to the stakeholders? (Provide 2-4 sentences detailing the significance, urgency, and potential consequences)
Who are the key people or groups affected? (Provide 2-4 sentences identifying primary and secondary stakeholders and their specific concerns)
What is clearly not part of the problem? (Provide 2-4 sentences clarifying boundaries and scope limitations)
What's the current situation? (Provide 2-4 sentences describing the present state, context, and immediate circumstances)

Phase 2: Break it Down
What are the key parts of this problem? (Provide 2-4 sentences identifying and describing the main components and sub-issues)
How are these parts connected? (Provide 2-4 sentences explaining relationships, dependencies, and interconnections)
Are there any hidden causes or unseen factors? (Provide 2-4 sentences exploring underlying issues, systemic factors, and root causes)
What similar problems could offer ideas? (Provide 2-4 sentences identifying comparable situations, precedents, and analogous challenges)

Phase 3: Assess the Information
What info do we already have? (Provide 2-4 sentences summarizing available data, knowledge, and reliable sources)
What's missing? (Provide 2-4 sentences identifying gaps, unknowns, and areas requiring further investigation)
What would help us understand better? (Provide 2-4 sentences specifying types of information, research, or analysis needed)
How could we gather the missing info? (Provide 2-4 sentences outlining methods, resources, and approaches for data collection)

Phase 4: Explore Solutions
Should we go big or start small? (Provide 2-4 sentences comparing comprehensive vs. incremental approaches and their trade-offs)
What ideas are worth exploring? (Provide 2-4 sentences presenting potential solutions, strategies, and innovative approaches)
Have others solved similar problems? (Provide 2-4 sentences referencing successful examples, best practices, and lessons learned)
What would a great solution look like? (Provide 2-4 sentences describing ideal outcomes, success criteria, and desired characteristics)
What results are we aiming for? (Provide 2-4 sentences defining specific goals, metrics, and expected impacts)

Phase 5: Plan to Act
What are the key next steps? (Provide 2-4 sentences outlining immediate actions, priorities, and logical sequence)
Who needs to be involved? (Provide 2-4 sentences identifying key players, decision-makers, and implementation teams)
What's a realistic timeline? (Provide 2-4 sentences proposing timeframes, milestones, and scheduling considerations)
What do we need (people, money, tools)? (Provide 2-4 sentences specifying resource requirements, capabilities, and support needed)
How will we know it's working? (Provide 2-4 sentences establishing success indicators, monitoring methods, and evaluation criteria)

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