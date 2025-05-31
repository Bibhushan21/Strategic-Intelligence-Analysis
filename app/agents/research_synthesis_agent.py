from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import json
import re


logger = logging.getLogger(__name__)


class ResearchSynthesisAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.timeout = 120  # Increased timeout

    def get_system_prompt(self) -> str:
        return """You are the Research Synthesis Agent. Your job is to analyze the full body of research—including the original challenge statement and all outputs from the following agents:

Problem Explorer Agent

Best Practices Agent

Horizon Scanning Agent

Scenario Planning Agent (GBN & Change Progression)

Your goal is to synthesize all inputs and extract the most important, actionable insights that can inform solution development and strategic decisions.

✍️ Section-by-Section Instructions
📌 Section 1: Key Insights
Extract the most critical, decision-ready findings

Each point must offer actionable value, not just observation

Ask:

What has our combined research taught us?

How can that insight be acted on?

🚀 Section 2: Opportunity Spaces
Identify areas of high potential for innovation or impact

Relate them to research and scenarios where relevant

Ask:

Where are the biggest levers for change?

What needs or gaps are most urgent?

⚠️ Section 3: Risk & Resilience
List risks or uncertainties revealed by the research

Recommend practical strategies to absorb or adapt

Ask:

What could go wrong?

How can we build resilience?

💡 Section 4: Innovation Pathways
Point out where current solutions are failing

Suggest emerging technologies or ideas that enable transformation

Ask:

Where can we move beyond the status quo?

What innovation can unlock new possibilities?

📆 Section 5: Quick Wins vs Long-Term Strategies
Identify actions we can take now

Also outline strategic foundations for the future

Ask:

What's urgent and doable right away?

What needs deeper setup but must start now?

✅ Guidelines
Output must be fully structured, not freeform text

All insights must be grounded in research and scenarios

Avoid duplication or repetition from source agents

Prioritize strategic clarity, impact, and practical use
"""


    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        problem_explorer_data = input_data.get('problem_explorer', {}).get('data', {}).get('structured_output', {})
        problem_definition_text = "N/A"
        if problem_explorer_data:
            phase1_content = problem_explorer_data.get('phase1', {}).get('content', [])
            if phase1_content:
                problem_definition_text = "\n".join(phase1_content)
            elif problem_explorer_data.get('acknowledgment'):
                problem_definition_text = problem_explorer_data.get('acknowledgment')

        best_practices_data = input_data.get('best_practices', {}).get('data', {})
        best_practices_list = best_practices_data.get('structured_practices', []) 

        # Horizon scanning data - current structure is likely raw text due to user revert
        horizon_scan_raw_data = input_data.get('horizon_scanning', {}).get('data', {}).get('raw_sections', {})
        horizon_scan_text = "N/A"
        if isinstance(horizon_scan_raw_data, dict) and 'raw_response' in horizon_scan_raw_data: # Assuming old structure post-revert
            horizon_scan_text = horizon_scan_raw_data.get('raw_response', 'Horizon scan data not available or in unexpected format.')
        elif isinstance(horizon_scan_raw_data, str): # If raw_sections became just the string itself
             horizon_scan_text = horizon_scan_raw_data
        elif horizon_scan_raw_data: # If it's some other dict, try to stringify for now
            horizon_scan_text = json.dumps(horizon_scan_raw_data, indent=2)


        # Scenario Planning data - access the new detailed structure
        scenario_planning_output = input_data.get('scenario_planning', {}).get('data', {}).get('structured_scenario_output', {})
        gbn_scenarios = scenario_planning_output.get('gbn_scenarios', [])
        change_progression_scenarios = scenario_planning_output.get('change_progression_scenarios', [])

        scenarios_summary_text = "Scenario summaries not available or not parsed."
        if gbn_scenarios or change_progression_scenarios:
            scenarios_summary_text = "Key Scenarios Identified:\n"
            if gbn_scenarios:
                scenarios_summary_text += "\nGBN Framework Scenarios:\n"
                for s in gbn_scenarios[:2]: # Summarize first 2 GBN
                    scenarios_summary_text += f"- Title: {s.get('title', 'N/A')} (Position: {s.get('matrix_position', 'N/A')})\n  Description (brief): {s.get('description', 'N/A')[:100]}...\n"
            if change_progression_scenarios:
                scenarios_summary_text += "\nChange Progression Model Scenarios:\n"
                for s in change_progression_scenarios[:2]: # Summarize first 2 CP
                    scenarios_summary_text += f"- Title: {s.get('title', 'N/A')} (Level: {s.get('level', 'N/A')})\n  Description (brief): {s.get('description', 'N/A')[:100]}...\n"

        # Format best practices
        best_practices_text = "\n".join([f"- {p.get('title','N/A')}: {p.get('description','N/A')}" for p in best_practices_list[:2]]) if best_practices_list else "N/A"

        return f"""Synthesize the following research findings for the strategic question: {input_data.get('strategic_question', 'N/A')}

Problem Definition Context:
{problem_definition_text}

Key Best Practices Identified:
{best_practices_text}

Horizon Scanning Insights (Raw, as available):
{horizon_scan_text}

{scenarios_summary_text}

Additional Instructions from user: {input_data.get('prompt', 'N/A')}

Please provide a comprehensive synthesis following the 5-section structure outlined in your system prompt (Key Insights, Opportunity Spaces, Risk & Resilience, Innovation Pathways, Quick Wins vs Long-Term Strategies).
Ensure all insights are grounded in the provided research and scenarios.
"""


    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
           
            # New parsing logic for the 5 sections
            parsed_data = {
                "key_insights": [],
                "opportunity_spaces": [],
                "risk_and_resilience": [],
                "innovation_pathways": [],
                "quick_wins_vs_long_term": []
            }
           
            current_section_key = None
            section_headers = {
                "📌 Section 1: Key Insights": "key_insights",
                "Section 1: Key Insights": "key_insights",
                "Key Insights": "key_insights",
                
                "🚀 Section 2: Opportunity Spaces": "opportunity_spaces",
                "Section 2: Opportunity Spaces": "opportunity_spaces",
                "Opportunity Spaces": "opportunity_spaces",

                "⚠️ Section 3: Risk & Resilience": "risk_and_resilience",
                "Section 3: Risk & Resilience": "risk_and_resilience",
                "Risk & Resilience": "risk_and_resilience",

                "💡 Section 4: Innovation Pathways": "innovation_pathways",
                "Section 4: Innovation Pathways": "innovation_pathways",
                "Innovation Pathways": "innovation_pathways",

                "📆 Section 5: Quick Wins vs Long-Term Strategies": "quick_wins_vs_long_term",
                "Section 5: Quick Wins vs Long-Term Strategies": "quick_wins_vs_long_term",
                "Quick Wins vs Long-Term Strategies": "quick_wins_vs_long_term"
            }

            buffer = []
            for line in response.split('\n'):
                stripped_line = line.strip()
                
                matched_header = False
                for header, key in section_headers.items():
                    if header in stripped_line: # Using "in" for flexibility with potential leading/trailing chars
                        if current_section_key and buffer: # Save previous section's buffer
                            parsed_data[current_section_key].extend([l.strip() for l in buffer if l.strip()])
                            buffer = []
                        current_section_key = key
                        # Remove the header itself from the line if it's the only content or starts the line
                        content_after_header = stripped_line.replace(header, "").strip()
                        if content_after_header:
                            buffer.append(content_after_header)
                        matched_header = True
                        break # Move to next line once header is processed
                
                if matched_header:
                    continue
               
                if current_section_key and stripped_line: # Add non-header lines to current section's buffer
                    buffer.append(stripped_line)
                elif current_section_key and not stripped_line and buffer: # Keep empty lines if they are part of a paragraph in buffer
                    buffer.append("") # Preserve paragraph breaks
            
            if current_section_key and buffer: # Save the last section's buffer
                parsed_data[current_section_key].extend([l.strip() for l in buffer if l.strip() or l == ""]) # Keep preserved empty lines if any
                # Clean up trailing empty strings if any from paragraph preservation
                while parsed_data[current_section_key] and parsed_data[current_section_key][-1] == "":
                    parsed_data[current_section_key].pop()
           
            return self.format_output(parsed_data) # Pass the new parsed_data structure
           
        except Exception as e:
            logger.error(f"Error in ResearchSynthesisAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }


    def format_output(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way based on the new 5-section parsing."""
        try:
            markdown_output = "# Research Synthesis\n\n"
            
            section_titles_map = {
                "key_insights": "📌 Key Insights",
                "opportunity_spaces": "🚀 Opportunity Spaces",
                "risk_and_resilience": "⚠️ Risk & Resilience",
                "innovation_pathways": "💡 Innovation Pathways",
                "quick_wins_vs_long_term": "📆 Quick Wins vs Long-Term Strategies"
            }

            for section_key, display_title in section_titles_map.items():
                if parsed_data.get(section_key):
                    markdown_output += f"## {display_title}\n\n"
                    for item in parsed_data[section_key]:
                        # Assume items are pre-stripped; add bullet if not already a list item marker
                        if item.startswith("-") or item.startswith("*") or item.startswith("•") or item.isdigit():
                            markdown_output += f"{item}\n"
                        else:
                            markdown_output += f"- {item}\n"
                markdown_output += "\n"
            
            if not any(parsed_data.get(key) for key in section_titles_map): # Fallback if all sections are empty
                markdown_output += "No structured insights were synthesized. Please review the raw LLM response if available."
                raw_response_text = parsed_data.get("raw_response_llm", "") # Assuming process might pass this for fallback
                if raw_response_text : markdown_output += "\n\nRaw LLM Output (if available): \n" + raw_response_text

            logger.info(f"Formatted Research Synthesis Output (markdown length: {len(markdown_output)})")
            
            return {
                "status": "success",
                "data": {
                    "structured_synthesis": parsed_data, # New key for the full structured data
                    "raw_sections": parsed_data, # For backward compatibility if anything used old raw_sections as the dict itself
                    "formatted_output": markdown_output,
                    # "raw_response_llm": parsed_data.get("raw_response_llm") # If passed from process for fallback
                }
            }
        except Exception as e:
            logger.error(f"Error formatting Research Synthesis output: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "data": {
                    "formatted_output": f"# Research Synthesis\n\nError formatting output: {str(e)}",
                    # "raw_response_llm": parsed_data.get("raw_response_llm")
                }
            }
