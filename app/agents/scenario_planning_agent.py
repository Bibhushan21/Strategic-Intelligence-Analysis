from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import json
import re # For parsing

logger = logging.getLogger(__name__)

class ScenarioPlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.timeout = 120  # Increased timeout

    def get_system_prompt(self) -> str:
        return """You are the Scenario Planning Agent. Your task is to analyze a given problem statement and generate 8 well-structured future scenarios using two strategic foresight frameworks:

🌐 1. GBN Framework (Global Business Network)
Identify 2 critical uncertainties or weak signals that could strongly shape the future of the problem.

Place one uncertainty on the X-axis and one on the Y-axis to form a 2x2 matrix.

Use the 4 quadrants to create 4 distinct future scenarios, each based on a different combination of the two uncertainties.

For each scenario, include:

title: A short, creative name for the scenario

matrix_position: A1, A2, B1, or B2 (indicating quadrant)

description: A narrative (150–300 words) that describes how this future might unfold and how it affects the original challenge

🔁 2. Change Progression Model
Choose 1 key uncertainty or weak signal.

Show how it might evolve over 4 levels of change:

No Change – Business as usual

Marginal Change – Small, gradual shifts

Adaptive Change – Big, strategic adjustments

Radical Change – Disruptive, transformational change

For each level, include:

level: Change level name (No, Marginal, Adaptive, Radical)

title: A creative title that reflects the future

description: A scenario (150–300 words) that shows how the system evolves and the effects of the change


🧠 Notes for Writing
All scenarios must be realistic, internally consistent, and clearly based on the original problem statement.

Use engaging but clear language so that decision-makers can visualize each future.

Avoid repetition, and ensure that each scenario is meaningfully distinct.
"""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        time_frame = input_data.get('time_frame', 'N/A')
        region = input_data.get('region', 'N/A')
        
        problem_explorer_data = input_data.get('problem_explorer', {}).get('data', {}).get('structured_output', {})
        problem_context = "N/A"
        if problem_explorer_data:
            phase1_content = problem_explorer_data.get('phase1', {}).get('content', [])
            if phase1_content:
                problem_context = "\n".join(phase1_content)
            elif problem_explorer_data.get('acknowledgment'):
                problem_context = problem_explorer_data.get('acknowledgment')
            else:
                problem_context = str(problem_explorer_data.get('phase1', 'Problem details not clearly defined in Phase 1.'))
        
        return f"""Create distinct scenarios for the following strategic challenge:

Strategic Question: {strategic_question}
Time Frame: {time_frame}
Region/Scope: {region}
Problem Context: 
{problem_context}

Please generate 8 scenarios according to the two specified frameworks (GBN and Change Progression Model) based on the problem context and strategic question provided.
Ensure all requested fields for each scenario type are present and distinct. Adhere to the word counts for descriptions.
"""

    def _parse_multi_framework_scenarios(self, response_text: str) -> Dict[str, List[Dict[str, Any]]]:
        parsed_output = {
            "gbn_scenarios": [],
            "change_progression_scenarios": []
        }
        
        # Normalize line endings and split into lines
        lines = response_text.replace('\\r\\n', '\\n').split('\\n')
        
        current_framework = None
        current_scenario = None
        description_buffer = []

        def save_current_scenario():
            nonlocal current_scenario, description_buffer
            if current_scenario:
                if description_buffer:
                    current_scenario['description'] = "".join(description_buffer).strip()
                    description_buffer = []
                if current_framework == "gbn" and 'title' in current_scenario: # Ensure required fields
                    parsed_output["gbn_scenarios"].append(current_scenario)
                elif current_framework == "change_progression" and 'title' in current_scenario: # Ensure required fields
                    parsed_output["change_progression_scenarios"].append(current_scenario)
            current_scenario = None

        for line in lines:
            stripped_line = line.strip()

            if not stripped_line and not description_buffer: # Skip empty lines unless in a description
                continue

            if "🌐 1. GBN Framework" in line or "1. GBN Framework" in line:
                save_current_scenario()
                current_framework = "gbn"
                continue
            elif "🔁 2. Change Progression Model" in line or "2. Change Progression Model" in line:
                save_current_scenario()
                current_framework = "change_progression"
                continue

            if current_framework:
                title_match_gbn = re.match(r"title:\s*(.*)", stripped_line, re.IGNORECASE)
                matrix_pos_match = re.match(r"matrix_position:\s*(.*)", stripped_line, re.IGNORECASE)
                
                level_match_cp = re.match(r"level:\s*(.*)", stripped_line, re.IGNORECASE)
                title_match_cp = re.match(r"title:\s*(.*)", stripped_line, re.IGNORECASE) # Can be same as GBN title

                description_marker = re.match(r"description:\s*(.*)", stripped_line, re.IGNORECASE)

                is_new_field = False

                if current_framework == "gbn":
                    if title_match_gbn:
                        save_current_scenario()
                        current_scenario = {"title": title_match_gbn.group(1).strip()}
                        is_new_field = True
                    elif current_scenario and matrix_pos_match:
                        current_scenario["matrix_position"] = matrix_pos_match.group(1).strip()
                        is_new_field = True
                
                elif current_framework == "change_progression":
                    if level_match_cp:
                        save_current_scenario() # Level starts a new scenario in CP model
                        current_scenario = {"level": level_match_cp.group(1).strip()}
                        is_new_field = True
                    elif current_scenario and title_match_cp: # title comes after level for CP
                        current_scenario["title"] = title_match_cp.group(1).strip()
                        is_new_field = True

                if description_marker:
                    if current_scenario: # Ensure description belongs to a scenario
                        # If there was content on the same line as "description:"
                        if description_buffer: # Save previous description line if any
                             current_scenario['description'] = "".join(description_buffer).strip()
                        description_buffer = [description_marker.group(1).strip() + "\n"] if description_marker.group(1).strip() else ["\n"]
                    is_new_field = True # Counts as a new field, stops appending to previous description
                elif is_new_field and description_buffer: # A new field started, finalize previous description
                    if current_scenario and 'description' not in current_scenario: # Avoid overwriting if desc marker had content
                        current_scenario['description'] = "".join(description_buffer).strip()
                    description_buffer = []
                elif not is_new_field and current_scenario: # No new field, and we are in a scenario
                    if description_buffer or (current_scenario and 'description' in current_scenario and not description_buffer): # continue description
                        description_buffer.append(line + "\n") # Add raw line with newline for multiline
                
                if is_new_field and len(description_buffer) > 0 and not description_marker : # if a non-description field started, save previous buffer
                    if current_scenario and 'description' not in current_scenario:
                         current_scenario['description'] = "".join(description_buffer).strip()
                    description_buffer = []


        save_current_scenario() # Save the last scenario
        logger.info(f"Parsed Scenario Data: GBN={len(parsed_output['gbn_scenarios'])}, CP={len(parsed_output['change_progression_scenarios'])}")
        return parsed_output

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            parsed_scenarios = self._parse_multi_framework_scenarios(response)
            
            # Log the structured output for verification
            # logger.info(f"Structured Scenario Output:\n{json.dumps(parsed_scenarios, indent=2)}")
            
            return self.format_output({
                "raw_response": response, # Keep raw response if needed
                "structured_scenarios": parsed_scenarios
            })
            
        except Exception as e:
            logger.error(f"Error in ScenarioPlanningAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        structured_scenarios = data.get("structured_scenarios", {
            "gbn_scenarios": [], "change_progression_scenarios": []
        })
        raw_response = data.get("raw_response", "") # Get raw_response for fallback or partial display

        markdown_output = "# Scenario Planning Analysis\n\n"

        markdown_output += "## 🌐 GBN Framework Scenarios\n\n"
        if structured_scenarios["gbn_scenarios"]:
            for i, scenario in enumerate(structured_scenarios["gbn_scenarios"], 1):
                markdown_output += f"### GBN Scenario {i}: {scenario.get('title', 'N/A')}\n\n"
                markdown_output += f"**Matrix Position:** {scenario.get('matrix_position', 'N/A')}\n\n"
                markdown_output += f"**Description:**\n{scenario.get('description', 'N/A')}\n\n---\n\n"
        else:
            markdown_output += "No GBN scenarios were parsed or generated.\n\n"
        
        markdown_output += "## 🔁 Change Progression Model Scenarios\n\n"
        if structured_scenarios["change_progression_scenarios"]:
            for i, scenario in enumerate(structured_scenarios["change_progression_scenarios"], 1):
                markdown_output += f"### Change Progression Scenario {i}: {scenario.get('title', 'N/A')} ({scenario.get('level', 'N/A')})\n\n"
                markdown_output += f"**Level:** {scenario.get('level', 'N/A')}\n\n"
                markdown_output += f"**Description:**\n{scenario.get('description', 'N/A')}\n\n---\n\n"
        else:
            markdown_output += "No Change Progression scenarios were parsed or generated.\n\n"

        # Fallback for markdown if parsing somehow failed badly but we have a raw response
        if not structured_scenarios["gbn_scenarios"] and not structured_scenarios["change_progression_scenarios"] and raw_response:
            logger.warn("Scenario parsing resulted in empty structured data; using raw response for markdown.")
            markdown_output = "# Scenario Planning Analysis)\n\n" + raw_response

        
        return {
            "status": "success",
            "data": {
                # New structured output for downstream consumption
                "structured_scenario_output": structured_scenarios,
                # Retain raw_sections for now, but its 'scenarios' list will be from the old parser (empty/stale)
                # This 'raw_sections' part needs careful review if other agents depend on its old format.
                # For "perfect output" from THIS agent, structured_scenario_output is primary.
                "raw_sections": {"scenarios": [], "raw_response_text": raw_response}, # Placeholder for old structure
                "formatted_output": markdown_output,
                "raw_response_llm": raw_response # Explicitly save the raw LLM output
            }
            }