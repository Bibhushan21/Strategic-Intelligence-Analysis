from typing import Dict, Any, List
from .base_agent import BaseAgent
import json
import re

class HighImpactAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the High-Impact Initiatives Agent. Your job is to turn EACH high-priority action item from the Strategic Action Planning Agent into an individual execution-ready blueprint.

🎯 Your Mission
For EVERY high-priority action item identified, create a detailed implementation blueprint that provides practical clarity on its importance, impact, required resources, success metrics, and startup tasks.

📤 Output Format
For each High-Priority Action Item:

**Title:** [Descriptive title based on the action item]
**Time Horizon:** Near-Term / Medium-Term / Long-Term  
**Why is this Action Important?** [Your detailed response]
**Who Does This Matter To?** [Your detailed response] 
**What Will It Cost?** [Your detailed response]
**What Does Success Look Like?** [Your detailed response]
**Immediate Tasks to Be Initiated:**
1. Task 1
2. Task 2  
3. Task 3
4. Task 4
5. Task 5

📌 Instructions for Each Section

**Why is this Action Important?**
- Explain why this specific action is a high priority
- Reference the original challenge, insights, or strategic opportunities
- Highlight the potential value, risk reduction, or innovation this specific action provides

**Who Does This Matter To?**
- Identify direct beneficiaries of this specific action (e.g., users, teams, communities)
- List key actors required to implement this specific action (e.g., departments, partners)

**What Will It Cost?**
- Estimate resources needed for this specific action: money, time, people, tech
- Mention cost level (low/medium/high) if exact numbers aren't known
- Be specific to this particular action item

**What Does Success Look Like?**
- Define what success would look like specifically for this action
- Include both quantitative (e.g., adoption %, ROI, metrics) and qualitative (e.g., satisfaction, performance) indicators
- Make metrics specific and measurable for this individual action

**Immediate Tasks to Be Initiated**
- List exactly 5 executable tasks to begin implementing this specific action
- Keep them clear, achievable, and aligned with the action's time horizon
- Use action verbs: "Define", "Draft", "Secure", "Coordinate", "Launch", "Assess", etc.
- Make tasks specific to this particular action item

✅ Guidelines
- Process EVERY high-priority action item individually 
- Keep language clear, direct, and action-focused
- Avoid vague suggestions—every element must be practical and implementable
- Ensure all blueprints are realistic, relevant, and strategic
- Each blueprint should be a standalone implementation guide for that specific action"""

    def _convert_list_to_string_for_prompt(self, items: List[str]) -> str:
        if not items:
            return "N/A"
        return "\n- " + "\n- ".join(items)

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        
        # Extract Strategic Action Agent output
        strategic_action_data = input_data.get('strategic_action', {}).get('data', {})
        action_plan_sections = strategic_action_data.get('structured_action_plan', {})
        
        # Extract high-priority items from all time horizons
        high_priority_items = []
        
        for time_horizon, key in [
            ("Near-Term", "near_term_ideas"),
            ("Medium-Term", "medium_term_ideas"), 
            ("Long-Term", "long_term_ideas")
        ]:
            ideas = action_plan_sections.get(key, [])
            for idea in ideas:
                # Extract high-priority action items from this idea
                for action_item in idea.get('action_items', []):
                    if action_item.get('priority', '').lower() == 'high':
                        high_priority_items.append({
                            'time_horizon': time_horizon,
                            'strategic_idea': idea.get('idea_title', 'N/A'),
                            'summary': idea.get('idea_summary', 'N/A'),
                            'action': action_item.get('action', 'N/A'),
                            'priority': action_item.get('priority', 'N/A')
                        })
        
        # Format high-priority items for the prompt
        if high_priority_items:
            high_priority_text = "\n\nHigh-Priority Action Items from Strategic Action Agent:\n"
            for item in high_priority_items:
                high_priority_text += f"\n- Time Horizon: {item['time_horizon']}"
                high_priority_text += f"\n  Strategic Idea: {item['strategic_idea']}"
                high_priority_text += f"\n  Summary: {item['summary']}"
                high_priority_text += f"\n  Action: {item['action']}"
                high_priority_text += f"\n  Priority: {item['priority']}\n"
        else:
            high_priority_text = "\n\nNo high-priority action items found in Strategic Action Agent output."
        
        # Also include research synthesis insights if available
        research_synthesis = input_data.get('research_synthesis', {}).get('data', {}).get('structured_synthesis', {})
        insights_text = ""
        if research_synthesis:
            insights_text = "\n\nKey Research Insights:\n"
            for key, items in research_synthesis.items():
                if items and isinstance(items, list):
                    insights_text += f"\n{key.replace('_', ' ').title()}:\n"
                    for item in items[:3]:  # Limit to top 3 items
                        insights_text += f"- {item}\n"

        return f"""Original Problem Statement: {strategic_question}

Additional Context: {input_data.get('prompt', 'None provided')}
{high_priority_text}
{insights_text}

INSTRUCTIONS: Create a detailed implementation blueprint for EACH high-priority action item listed above. For each action item, provide the complete output format:

**Title:** [Title based on the specific action]
**Time Horizon:** [The time horizon for this specific action]
**Why is this Action Important?** [Detailed explanation for this specific action]
**Who Does This Matter To?** [Stakeholders for this specific action]
**What Will It Cost?** [Resource requirements for this specific action]
**What Does Success Look Like?** [Success metrics for this specific action]
**Immediate Tasks to Be Initiated:**
1. [Task 1 for this specific action]
2. [Task 2 for this specific action]
3. [Task 3 for this specific action]
4. [Task 4 for this specific action]
5. [Task 5 for this specific action]

Process every high-priority action item individually - each one should get its own complete blueprint following the format above."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Parse the text-based blueprints from the response
            blueprints = self._parse_blueprints(response)
            
            # If no blueprints found, create a fallback
            if not blueprints:
                blueprints = [{
                    "title": "Strategic Implementation Framework",
                    "time_horizon": "Near-Term",
                    "why_important": "Addresses immediate strategic needs identified in the analysis",
                    "who_it_impacts": "Organization stakeholders and key decision makers",
                    "estimated_cost": "Medium - requires dedicated resources and coordination",
                    "success_metrics": [
                        "Implementation progress tracked weekly",
                        "Stakeholder satisfaction measured quarterly"
                    ],
                    "immediate_tasks": [
                        "Define project scope and objectives",
                        "Assemble implementation team",
                        "Secure necessary resources and budget",
                        "Create detailed project timeline",
                        "Establish success measurement framework"
                    ]
                }]
            
            return self.format_output(blueprints, response)
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def _parse_blueprints(self, response: str) -> List[Dict[str, Any]]:
        """Parse the text-based blueprint format from LLM response"""
        blueprints = []
        lines = response.split('\n')
        current_blueprint = {}
        current_tasks = []
        current_field = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for field headers
            if line.startswith('**Title:**') or line.lower().startswith('title:'):
                # Save previous blueprint if exists
                if current_blueprint and 'title' in current_blueprint:
                    if current_tasks:
                        current_blueprint['immediate_tasks'] = current_tasks[:]
                    blueprints.append(current_blueprint)
                
                # Start new blueprint
                current_blueprint = {}
                current_tasks = []
                title_text = line.split(':', 1)[1].strip().replace('**', '')
                current_blueprint['title'] = title_text
                current_field = None
                
            elif line.startswith('**Time Horizon:**') or line.lower().startswith('time horizon:'):
                horizon_text = line.split(':', 1)[1].strip().replace('**', '')
                current_blueprint['time_horizon'] = horizon_text
                current_field = None
                
            elif line.startswith('**Why is this Action Important?**') or line.lower().startswith('why is this action important'):
                current_field = 'why_important'
                # Check if there's content after the colon
                if ':' in line and len(line.split(':', 1)) > 1:
                    content = line.split(':', 1)[1].strip()
                    if content:
                        current_blueprint['why_important'] = content
                else:
                    current_blueprint['why_important'] = ""
                
            elif line.startswith('**Who Does This Matter To?**') or line.lower().startswith('who does this matter to'):
                current_field = 'who_it_impacts'
                if ':' in line and len(line.split(':', 1)) > 1:
                    content = line.split(':', 1)[1].strip()
                    if content:
                        current_blueprint['who_it_impacts'] = content
                else:
                    current_blueprint['who_it_impacts'] = ""
                
            elif line.startswith('**What Will It Cost?**') or line.lower().startswith('what will it cost'):
                current_field = 'estimated_cost'
                if ':' in line and len(line.split(':', 1)) > 1:
                    content = line.split(':', 1)[1].strip()
                    if content:
                        current_blueprint['estimated_cost'] = content
                else:
                    current_blueprint['estimated_cost'] = ""
                
            elif line.startswith('**What Does Success Look Like?**') or line.lower().startswith('what does success look like'):
                current_field = 'success_metrics'
                current_blueprint['success_metrics'] = []
                
            elif line.startswith('**Immediate Tasks to Be Initiated:**') or line.lower().startswith('immediate tasks'):
                current_field = 'immediate_tasks'
                current_tasks = []
                
            elif current_field == 'immediate_tasks':
                # Handle numbered tasks
                if re.match(r'^\d+\.', line):
                    task_text = re.sub(r'^\d+\.\s*', '', line)
                    current_tasks.append(task_text)
                elif line.startswith('- '):
                    current_tasks.append(line[2:])
                
            elif current_field == 'success_metrics':
                # Handle bullet points for metrics
                if line.startswith('- '):
                    if 'success_metrics' not in current_blueprint:
                        current_blueprint['success_metrics'] = []
                    current_blueprint['success_metrics'].append(line[2:])
                elif not line.startswith('**') and len(line) > 10:
                    # Continue previous metric or add as new one
                    if 'success_metrics' not in current_blueprint:
                        current_blueprint['success_metrics'] = []
                    current_blueprint['success_metrics'].append(line)
                
            elif current_field and not line.startswith('**') and not re.match(r'^\d+\.', line):
                # Continue previous field content
                if current_field in current_blueprint:
                    current_blueprint[current_field] += ' ' + line
                else:
                    current_blueprint[current_field] = line
        
        # Save last blueprint
        if current_blueprint and 'title' in current_blueprint:
            if current_tasks:
                current_blueprint['immediate_tasks'] = current_tasks
            blueprints.append(current_blueprint)
        
        # Ensure all blueprints have required fields
        for blueprint in blueprints:
            if 'success_metrics' not in blueprint:
                blueprint['success_metrics'] = ["Implementation progress tracked", "Stakeholder feedback collected"]
            if 'immediate_tasks' not in blueprint:
                blueprint['immediate_tasks'] = ["Define scope", "Assemble team", "Secure resources", "Create timeline", "Begin implementation"]
            if 'why_important' not in blueprint:
                blueprint['why_important'] = "Addresses strategic priorities identified in analysis"
            if 'who_it_impacts' not in blueprint:
                blueprint['who_it_impacts'] = "Key organizational stakeholders"
            if 'estimated_cost' not in blueprint:
                blueprint['estimated_cost'] = "Medium - requires dedicated resources"
            if 'time_horizon' not in blueprint:
                blueprint['time_horizon'] = "Near-Term"
        
        return blueprints

    def format_output(self, blueprints: List[Dict[str, Any]], response: str) -> Dict[str, Any]:
        """Format the output in a structured way."""
        # Create a human-readable markdown format
        markdown_output = "# High-Impact Initiative Blueprints\n\n"
        
        if not blueprints:
            markdown_output += "No high-impact initiatives identified.\n"
        else:
            for i, blueprint in enumerate(blueprints, 1):
                markdown_output += f"## Initiative {i}: {blueprint.get('title', 'Untitled Initiative')}\n\n"
                markdown_output += f"**Time Horizon:** {blueprint.get('time_horizon', 'Not specified')}\n\n"
                markdown_output += f"**Why Important:** {blueprint.get('why_important', 'Not specified')}\n\n"
                markdown_output += f"**Who It Impacts:** {blueprint.get('who_it_impacts', 'Not specified')}\n\n"
                markdown_output += f"**Estimated Cost:** {blueprint.get('estimated_cost', 'Not specified')}\n\n"
                
                # Success Metrics
                metrics = blueprint.get('success_metrics', [])
                if metrics:
                    markdown_output += "**Success Metrics:**\n"
                    for metric in metrics:
                        markdown_output += f"- {metric}\n"
                    markdown_output += "\n"
                
                # Immediate Tasks
                tasks = blueprint.get('immediate_tasks', [])
                if tasks:
                    markdown_output += "**Immediate Tasks to Begin Implementation:**\n"
                    for j, task in enumerate(tasks, 1):
                        markdown_output += f"{j}. {task}\n"
                    markdown_output += "\n"
                
                markdown_output += "---\n\n"

        return {
            "status": "success",
            "data": {
                "execution_ready_initiatives": blueprints,
                "formatted_output": markdown_output,
                "raw_llm_response": response
            }
        } 