from typing import Dict, Any, List
from .base_agent import BaseAgent
import json
import re
import logging

logger = logging.getLogger(__name__)

class StrategicActionAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.timeout = 90  # Increased timeout for this complex agent

    def get_system_prompt(self) -> str:
        return """You are the Strategic Action Planning Agent. Your role is to convert synthesized insights into structured, time-bound, and prioritized strategic actions. Use the original problem statement and all outputs from the Research Synthesis Agent to build a practical roadmap for implementation across three timeframes.

🎯 Your Objective
Translate insights into concrete, high-impact actions across:

Near-Term (0–2 years): Quick wins, urgent needs, low complexity

Medium-Term (2–5 years): Planned, coordinated, realistic strategies

Long-Term (5–10 years): Visionary, systemic change with broad alignment

🧠 Input to Analyze
Original Problem Statement

Contextual constraints (if provided)

Synthesized findings from the Research Synthesis Agent, including:

Key Insights

Opportunity Spaces

Risk & Resilience

Innovation Pathways

Quick Wins vs Long-Term Strategies

🛠️ Instructions for Each Strategic Idea
Provide a title and 1–2 sentence summary of the idea.

Break it into 5 specific action items (clear, realistic, and time-horizon aligned).

Assign priority (High / Medium / Low) for each action based on:

Urgency

Potential impact

Feasibility

✅ Guidelines
Keep all actions solution-oriented, operationally defined, and sequenced.

Ensure each action aligns with the insights from the Research Synthesis Agent.

Focus on real-world execution, not abstract suggestions.

Use simple, direct language suitable for decision-makers and implementers.
"""

    def _convert_list_to_string_for_prompt(self, items: List[str]) -> str:
        if not items:
            return "N/A"
        return "\n- " + "\n- ".join(items)

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        contextual_constraints = input_data.get('prompt', 'None provided')

        synthesis_data = input_data.get('research_synthesis', {}).get('data', {}).get('structured_synthesis', {})
        
        synthesis_sections_text = "\n\nResearch Synthesis Agent Output:\n"
        
        section_titles_map = {
            "key_insights": "📌 Key Insights",
            "opportunity_spaces": "🚀 Opportunity Spaces",
            "risk_and_resilience": "⚠️ Risk & Resilience",
            "innovation_pathways": "💡 Innovation Pathways",
            "quick_wins_vs_long_term": "📆 Quick Wins vs Long-Term Strategies"
        }

        for key, title in section_titles_map.items():
            items = synthesis_data.get(key, [])
            if items:
                synthesis_sections_text += f"\n--- {title} ---\n"
                for item in items:
                    if isinstance(item, dict):
                         synthesis_sections_text += f"- {item.get('content', json.dumps(item))}\n"
                    else:
                         synthesis_sections_text += f"- {str(item)}\n"
            else:
                synthesis_sections_text += f"\n--- {title} ---\nNo specific points provided by Research Synthesis Agent for this section.\n"

        return f"""Original Problem Statement: {strategic_question}

Contextual Constraints (if any): {contextual_constraints}
{synthesis_sections_text}

Based on all the above information (Original Problem, Constraints, and the detailed Research Synthesis output), please generate strategic ideas and their specific action items according to the three time horizons (Near-Term, Medium-Term, Long-Term) and prioritization criteria outlined in your system instructions.
Focus on creating a practical and actionable roadmap.
"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            parsed_action_plan = {
                "near_term_ideas": [],
                "medium_term_ideas": [],
                "long_term_ideas": []
            }
            
            current_time_horizon_key = None
            current_strategic_idea = None
            action_item_buffer = [] # For collecting action item lines
            # Priority is expected per action, so it's part of action_item_buffer logic

            lines = response.split('\n')

            def save_current_strategic_idea():
                nonlocal current_strategic_idea, current_time_horizon_key, action_item_buffer
                if current_strategic_idea and current_strategic_idea.get('idea_title') and action_item_buffer:
                    # Finalize the last action item from buffer before saving idea
                    if len(action_item_buffer) > 0 and isinstance(action_item_buffer[-1], dict) and not action_item_buffer[-1].get('priority'):
                        # This implies an action was added but priority might be on next line or missed.
                        # For now, we assume priority is captured with action. If not, it will be None.
                        pass # No specific action if priority parsing is part of action text parsing
                    current_strategic_idea['action_items'] = [item for item in action_item_buffer if isinstance(item, dict)]
                
                if current_strategic_idea and current_strategic_idea.get('idea_title') and current_strategic_idea.get('action_items'):
                    if current_time_horizon_key:
                        parsed_action_plan[current_time_horizon_key].append(current_strategic_idea)
                    else:
                        logger.warn(f"Strategic idea '{current_strategic_idea.get('idea_title')}' found without a time horizon.")
                current_strategic_idea = None
                action_item_buffer = []
            
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                
                # 1. Time Horizon Detection
                if re.match(r"Near-Term\s*\(0\S*2\s*years\):?", stripped_line, re.IGNORECASE):
                    if current_strategic_idea: save_current_strategic_idea()
                    current_time_horizon_key = "near_term_ideas"
                    logger.debug(f"Switched to Near-Term horizon at line {i}")
                    continue
                elif re.match(r"Medium-Term\s*\(2\S*5\s*years\):?", stripped_line, re.IGNORECASE):
                    if current_strategic_idea: save_current_strategic_idea()
                    current_time_horizon_key = "medium_term_ideas"
                    logger.debug(f"Switched to Medium-Term horizon at line {i}")
                    continue
                elif re.match(r"Long-Term\s*\(5\S*10\s*years\):?", stripped_line, re.IGNORECASE):
                    if current_strategic_idea: save_current_strategic_idea()
                    current_time_horizon_key = "long_term_ideas"
                    logger.debug(f"Switched to Long-Term horizon at line {i}")
                    continue
                
                if not current_time_horizon_key: # Skip if not under a time horizon
                    continue
                
                # 2. Strategic Idea Detection (Title and Summary)
                # Assuming LLM might use "Strategic Idea: Title" or just "Title:"
                title_match = re.match(r"(?:Strategic Idea(?: Title)?:|Title:)\s*(.*)", stripped_line, re.IGNORECASE)
                if title_match:
                    if current_strategic_idea: save_current_strategic_idea() # Save previous idea
                    current_strategic_idea = {"idea_title": title_match.group(1).strip(), "idea_summary": "", "action_items": []}
                    action_item_buffer = [] # Reset for new idea
                    # Check if summary is on the next line or few lines
                    summary_buffer = []
                    for j in range(1, min(3, len(lines) - 1 - i)): # Look ahead 2 lines for summary
                        next_line_stripped = lines[i+j].strip()
                        if re.match(r"(?:\d+\.|-|\*|Action Item \d+:)", next_line_stripped, re.IGNORECASE) or \
                           re.match(r"(?:Strategic Idea(?: Title)?:|Title:)", next_line_stripped, re.IGNORECASE) or \
                           re.match(r"Priority:", next_line_stripped, re.IGNORECASE): \
                            break # Stop if we hit start of actions or new idea/section
                        if next_line_stripped : summary_buffer.append(next_line_stripped)
                    if summary_buffer:
                        current_strategic_idea["idea_summary"] = " ".join(summary_buffer)
                    continue # Processed title and potential summary

                # 3. Action Item Detection (within a strategic idea)
                if current_strategic_idea:
                    # Regex to capture action item text and its priority on the same or subsequent lines
                    # Example: "1. Action text (Priority: High)" or "- Action text\n  Priority: Medium"
                    action_match = re.match(r"(?:\d+\.|-|\*)\s*(.*?)(?:\(Priority:\s*(High|Medium|Low)\s*\))?", stripped_line, re.IGNORECASE)
                    
                    if action_match:
                        action_text = action_match.group(1).strip()
                        priority_from_action_line = action_match.group(2)
                        
                        current_action = {"action": action_text, "priority": None}
                        if priority_from_action_line:
                            current_action["priority"] = priority_from_action_line.strip()
                        
                        action_item_buffer.append(current_action)
                        # Check next line for priority if not found on current line
                        if not priority_from_action_line and (i + 1 < len(lines)):
                            next_line_priority_match = re.match(r"Priority:\s*(High|Medium|Low)", lines[i+1].strip(), re.IGNORECASE)
                            if next_line_priority_match and isinstance(action_item_buffer[-1], dict):
                                action_item_buffer[-1]["priority"] = next_line_priority_match.group(1).strip()
                                # We might want to advance 'i' here or mark next line as consumed, but loop will skip it if empty
                        continue # Done with this action line
                    elif action_item_buffer and isinstance(action_item_buffer[-1], dict) and not action_item_buffer[-1]["priority"]:
                        # Check if current line is a solo priority for the last action
                        priority_only_match = re.match(r"Priority:\s*(High|Medium|Low)", stripped_line, re.IGNORECASE)
                        if priority_only_match:
                            action_item_buffer[-1]["priority"] = priority_only_match.group(1).strip()
                            continue # Done with this priority line

            if current_strategic_idea: # Save any last idea under processing
                save_current_strategic_idea()
            
            return self.format_output(parsed_action_plan)
            
        except Exception as e:
            logger.error(f"Error in StrategicActionAgent.process: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, parsed_action_plan: Dict[str, Any]) -> Dict[str, Any]:
        markdown_output = "# Strategic Action Plan\n\n"
        time_horizon_map = {
            "near_term_ideas": "## Near-Term (0–2 years)",
            "medium_term_ideas": "## Medium-Term (2–5 years)",
            "long_term_ideas": "## Long-Term (5–10 years)"
        }

        any_ideas_found = False
        for key, title_markdown in time_horizon_map.items():
            ideas = parsed_action_plan.get(key, [])
            if ideas:
                any_ideas_found = True
                markdown_output += f"{title_markdown}\n\n"
                for i, idea in enumerate(ideas):
                    markdown_output += f"### Strategic Idea {i+1}: {idea.get('idea_title', 'N/A')}\n"
                    markdown_output += f"**Summary:** {idea.get('idea_summary', 'N/A')}\n\n"
                    markdown_output += "**Action Items:**\n"
                    action_items = idea.get('action_items', [])
                    if action_items:
                        for j, item in enumerate(action_items):
                            markdown_output += f"{j+1}. {item.get('action', 'N/A')} -- **Priority:** {item.get('priority', 'N/A')}\n"
                    else:
                        markdown_output += "- No specific action items identified for this idea.\n"
                    markdown_output += "\n"
            # else:
            #     markdown_output += f"{title_markdown}\n- No strategic ideas identified for this period.\n\n"

        if not any_ideas_found:
            markdown_output += "No strategic ideas were parsed or generated. Please review raw LLM output if available."
            # Consider adding raw LLM output here for debugging if process method passes it.

        return {
            "status": "success",
            "data": {
                "structured_action_plan": parsed_action_plan,
                "raw_sections": parsed_action_plan, # For some backward compatibility / simpler access if needed
                "formatted_output": markdown_output
            }
        } 