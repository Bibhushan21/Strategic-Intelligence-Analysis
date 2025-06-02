from typing import Dict, Any, List
from .base_agent import BaseAgent
import json
import re
import asyncio
import logging

logger = logging.getLogger(__name__)

class HighImpactAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # Increase timeout for High Impact Agent as it processes complex data
        self.timeout = 60  # Increase from 15 to 60 seconds
        self.max_retries = 2  # Reduce retries but increase timeout
        self.retry_delay = 2  # Increase retry delay

    def get_system_prompt(self) -> str:
        return """🚀 High-Impact Initiatives Agent — Create Exactly 3 Initiatives

You are the High-Impact Initiatives Agent. Your job is to create exactly 3 comprehensive initiatives - one for each time horizon (Near-Term, Medium-Term, Long-Term). Each initiative should combine ALL the high-priority actions within that time horizon into one strategic implementation plan.

📤 Output Format - Create Exactly 3 Initiatives:

**Title:** [Descriptive title for Near-Term initiative combining all near-term high-priority actions]
**Time Horizon:** Near-Term
**Why Important:** [Detailed explanation combining the strategic value of all near-term high-priority actions]
**Who It Impacts:** [Stakeholders affected by all near-term high-priority actions]
**Estimated Cost:** [Resource requirements for implementing all near-term high-priority actions]
**Success Metrics:**
- [Specific success metric 1 for near-term actions]
- [Specific success metric 2 for near-term actions]
- [Specific success metric 3 for near-term actions]

**Immediate Tasks:**
1. [Task that initiates multiple near-term high-priority actions]
2. [Task that initiates multiple near-term high-priority actions]
3. [Task that initiates multiple near-term high-priority actions]
4. [Task that initiates multiple near-term high-priority actions]
5. [Task that initiates multiple near-term high-priority actions]

**Title:** [Descriptive title for Medium-Term initiative combining all medium-term high-priority actions]
**Time Horizon:** Medium-Term
**Why Important:** [Detailed explanation combining the strategic value of all medium-term high-priority actions]
**Who It Impacts:** [Stakeholders affected by all medium-term high-priority actions]
**Estimated Cost:** [Resource requirements for implementing all medium-term high-priority actions]
**Success Metrics:**
- [Specific success metric 1 for medium-term actions]
- [Specific success metric 2 for medium-term actions] 
- [Specific success metric 3 for medium-term actions]

**Immediate Tasks:**
1. [Task that prepares for multiple medium-term high-priority actions]
2. [Task that prepares for multiple medium-term high-priority actions]
3. [Task that prepares for multiple medium-term high-priority actions]
4. [Task that prepares for multiple medium-term high-priority actions]
5. [Task that prepares for multiple medium-term high-priority actions]

**Title:** [Descriptive title for Long-Term initiative combining all long-term high-priority actions]
**Time Horizon:** Long-Term
**Why Important:** [Detailed explanation combining the strategic value of all long-term high-priority actions]
**Who It Impacts:** [Stakeholders affected by all long-term high-priority actions]
**Estimated Cost:** [Resource requirements for implementing all long-term high-priority actions]
**Success Metrics:**
- [Specific success metric 1 for long-term actions]
- [Specific success metric 2 for long-term actions]
- [Specific success metric 3 for long-term actions]

**Immediate Tasks:**
1. [Task that prepares for multiple long-term high-priority actions]
2. [Task that prepares for multiple long-term high-priority actions]
3. [Task that prepares for multiple long-term high-priority actions]
4. [Task that prepares for multiple long-term high-priority actions]
5. [Task that prepares for multiple long-term high-priority actions]

📌 Instructions:
- Create exactly 3 initiatives total
- Each initiative combines ALL high-priority actions within that time horizon
- Use specific, descriptive titles based on the actual high-priority actions
- Provide detailed, meaningful content - no generic responses
- Reference specific actions, stakeholders, and strategic outcomes
- Make each initiative comprehensive but focused on its time horizon"""

    def _convert_list_to_string_for_prompt(self, items: List[str]) -> str:
        if not items:
            return "N/A"
        return "\n- " + "\n- ".join(items)

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        
        # Extract Strategic Action Agent output
        strategic_action_data = input_data.get('strategic_action', {}).get('data', {})
        action_plan_sections = strategic_action_data.get('structured_action_plan', {})
        
        # Group high-priority items by time horizon
        high_priority_by_horizon = {
            "Near-Term": [],
            "Medium-Term": [],
            "Long-Term": []
        }
        
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
                        high_priority_by_horizon[time_horizon].append({
                            'strategic_idea': idea.get('idea_title', 'N/A'),
                            'idea_summary': idea.get('idea_summary', 'N/A'),
                            'action': action_item.get('action', 'N/A')
                        })
        
        # Format high-priority items by time horizon for creating 3 initiatives
        high_priority_text = "\n\nHigh-Priority Actions Grouped by Time Horizon (for creating 3 initiatives):\n"
        
        for horizon, actions in high_priority_by_horizon.items():
            high_priority_text += f"\n=== {horizon} High-Priority Actions ===\n"
            if actions:
                for i, action in enumerate(actions, 1):
                    high_priority_text += f"{i}. Strategic Idea: {action['strategic_idea']}\n"
                    high_priority_text += f"   Summary: {action['idea_summary']}\n"
                    high_priority_text += f"   Action: {action['action']}\n\n"
            else:
                high_priority_text += f"No high-priority actions identified for {horizon} timeframe.\n\n"
        
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

INSTRUCTIONS: Create exactly 3 comprehensive initiatives - one for each time horizon. Each initiative should combine ALL the high-priority actions within that time horizon into one strategic implementation plan.

For each time horizon that has high-priority actions, create ONE initiative using this format:

**Title:** [Descriptive title combining all actions in this time horizon]
**Time Horizon:** [Near-Term/Medium-Term/Long-Term]
**Why Important:** [Explain why ALL actions in this time horizon are strategically important]
**Who It Impacts:** [All stakeholders affected by actions in this time horizon]
**Estimated Cost:** [Combined resource requirements for all actions in this time horizon]
**Success Metrics:**
- [Metric 1 covering multiple actions]
- [Metric 2 covering multiple actions]
- [Metric 3 covering multiple actions]

**Immediate Tasks:**
1. [Task that initiates multiple actions in this time horizon]
2. [Task that initiates multiple actions in this time horizon]
3. [Task that initiates multiple actions in this time horizon]
4. [Task that initiates multiple actions in this time horizon]
5. [Task that initiates multiple actions in this time horizon]

Create exactly 3 initiatives total. Make titles specific and descriptive based on the actual high-priority actions in each time horizon."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"High Impact Agent starting with input keys: {list(input_data.keys())}")
            
            prompt = self.format_prompt(input_data)
            logger.info(f"Generated prompt length: {len(prompt)} characters")
            
            # Check if we have strategic action data
            strategic_action_data = input_data.get('strategic_action', {}).get('data', {})
            action_plan_sections = strategic_action_data.get('structured_action_plan', {})
            logger.info(f"Strategic action data keys: {list(strategic_action_data.keys())}")
            logger.info(f"Action plan sections keys: {list(action_plan_sections.keys())}")
            
            # Count high-priority items across all time horizons
            high_priority_count = 0
            for time_horizon, key in [
                ("Near-Term", "near_term_ideas"),
                ("Medium-Term", "medium_term_ideas"), 
                ("Long-Term", "long_term_ideas")
            ]:
                ideas = action_plan_sections.get(key, [])
                for idea in ideas:
                    for action_item in idea.get('action_items', []):
                        if action_item.get('priority', '').lower() == 'high':
                            high_priority_count += 1
            
            logger.info(f"Found {high_priority_count} high-priority action items to process")
            
            if high_priority_count == 0:
                logger.warning("No high-priority action items found, creating fallback")
                # If no strategic action data, create a basic response
                fallback_initiatives = [{
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
                
                return self.format_output(fallback_initiatives, "No strategic action data available - generated fallback response")
            
            # Try to get LLM response with better error handling
            try:
                logger.info("Invoking LLM for High Impact analysis...")
                response = await self.invoke_llm(prompt)
                logger.info(f"LLM response received, length: {len(response)} characters")
                    
            except asyncio.TimeoutError:
                logger.error("LLM request timed out, using fallback response")
                # Create fallback response for timeout
                fallback_initiatives = [{
                    "title": "Strategic Implementation Plan (Fallback)",
                    "time_horizon": "Near-Term",
                    "why_important": "Immediate action required based on strategic analysis - LLM processing timed out",
                    "who_it_impacts": "All identified stakeholders from strategic action plan",
                    "estimated_cost": "Medium - requires coordination of existing resources",
                    "success_metrics": [
                        "Initial implementation milestones achieved",
                        "Team coordination established successfully"
                    ],
                    "immediate_tasks": [
                        "Review strategic action recommendations",
                        "Identify immediate priority actions",
                        "Allocate team resources for implementation",
                        "Set up progress tracking systems",
                        "Begin execution of highest priority items"
                    ]
                }]
                
                return self.format_output(fallback_initiatives, "LLM timeout - generated fallback implementation plan")
            except Exception as llm_error:
                logger.error(f"LLM invocation failed: {str(llm_error)}")
                return {
                    "status": "error",
                    "error": f"LLM processing failed: {str(llm_error)}",
                    "agent_type": self.__class__.__name__
                }
            
            # Parse the text-based blueprints from the response
            blueprints = self._parse_blueprints(response)
            logger.info(f"Parsed {len(blueprints)} blueprints from LLM response")
            
            # Ensure we have exactly 3 initiatives (one per time horizon)
            if len(blueprints) != 3:
                logger.warning(f"Expected 3 initiatives but got {len(blueprints)}, creating standardized set")
                blueprints = [
                    {
                        "title": "Near-Term User Experience Enhancement",
                        "time_horizon": "Near-Term",
                        "why_important": "Immediate improvements to user experience and engagement through personalization and interface enhancements",
                        "who_it_impacts": "All users, UX/UI teams, engineering teams, data science teams",
                        "estimated_cost": "Medium - requires coordination of existing development resources",
                        "success_metrics": [
                            "User engagement metrics improve by 15% within 6 months",
                            "User interface satisfaction scores increase by 20%",
                            "Recommendation accuracy improvements measured quarterly"
                        ],
                        "immediate_tasks": [
                            "Conduct comprehensive user experience audit and gather feedback",
                            "Form cross-functional team for UI/UX improvements and personalization",
                            "Define success metrics and tracking systems for user engagement",
                            "Begin algorithm refinements and interface redesign planning",
                            "Establish A/B testing framework for continuous optimization"
                        ]
                    },
                    {
                        "title": "Medium-Term Content Strategy and Social Features",
                        "time_horizon": "Medium-Term",
                        "why_important": "Strategic expansion of content offerings and social engagement features to build competitive advantage",
                        "who_it_impacts": "Content teams, social feature developers, marketing teams, international users",
                        "estimated_cost": "High - requires significant investment in content acquisition and feature development",
                        "success_metrics": [
                            "Local content engagement increases by 25% in target markets",
                            "Social feature adoption reaches 30% of user base within 2 years",
                            "Content variety and satisfaction scores improve across all regions"
                        ],
                        "immediate_tasks": [
                            "Conduct market research for local content preferences and opportunities",
                            "Develop social features roadmap and technical requirements",
                            "Establish partnerships with local content providers and creators",
                            "Design community management and user engagement strategies",
                            "Create content acquisition and localization framework"
                        ]
                    },
                    {
                        "title": "Long-Term Strategic Partnerships and Innovation",
                        "time_horizon": "Long-Term",
                        "why_important": "Foundational partnerships and innovative content strategies for sustained competitive advantage",
                        "who_it_impacts": "Executive leadership, business development, content strategy teams, global partners",
                        "estimated_cost": "Very High - requires sustained investment and strategic partnerships",
                        "success_metrics": [
                            "Strategic partnerships established with 5+ major global content providers",
                            "Original content portfolio generates 40% of total engagement",
                            "Market leadership position established in 3+ new geographic regions"
                        ],
                        "immediate_tasks": [
                            "Identify and evaluate potential strategic partners for content creation",
                            "Develop long-term content strategy and original programming roadmap",
                            "Establish global content creation hubs and talent acquisition plans",
                            "Create partnership evaluation and negotiation framework",
                            "Design innovation labs for emerging content technologies and formats"
                        ]
                    }
                ]
            
            logger.info(f"High Impact Agent completed successfully with exactly {len(blueprints)} initiatives")
            return self.format_output(blueprints, response)
            
        except Exception as e:
            logger.error(f"Error in High Impact Agent: {str(e)}")
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
        current_metrics = []
        current_field = None
        
        for line in lines:
            line = line.strip()
            if not line or line == '---':
                continue
            
            # Check for field headers
            if line.startswith('**Title:**'):
                # Save previous blueprint if exists
                if current_blueprint and 'title' in current_blueprint:
                    if current_tasks:
                        current_blueprint['immediate_tasks'] = current_tasks[:]
                    if current_metrics:
                        current_blueprint['success_metrics'] = current_metrics[:]
                    blueprints.append(current_blueprint)
                
                # Start new blueprint
                current_blueprint = {}
                current_tasks = []
                current_metrics = []
                title_text = line.replace('**Title:**', '').strip()
                current_blueprint['title'] = title_text
                current_field = None
                
            elif line.startswith('**Time Horizon:**'):
                horizon_text = line.replace('**Time Horizon:**', '').strip()
                current_blueprint['time_horizon'] = horizon_text
                current_field = None
                
            elif line.startswith('**Why Important:**'):
                important_text = line.replace('**Why Important:**', '').strip()
                current_blueprint['why_important'] = important_text
                current_field = 'why_important'
                
            elif line.startswith('**Who It Impacts:**'):
                impacts_text = line.replace('**Who It Impacts:**', '').strip()
                if impacts_text:
                    current_blueprint['who_it_impacts'] = impacts_text
                else:
                    current_blueprint['who_it_impacts'] = ""
                current_field = 'who_it_impacts'
                
            elif line.startswith('**Estimated Cost:**'):
                cost_text = line.replace('**Estimated Cost:**', '').strip()
                current_blueprint['estimated_cost'] = cost_text
                current_field = 'estimated_cost'
                
            elif line.startswith('**Success Metrics:**'):
                current_field = 'success_metrics'
                current_metrics = []
                
            elif line.startswith('**Immediate Tasks:**'):
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
                    current_metrics.append(line[2:])
                elif not line.startswith('**') and len(line) > 10:
                    # Continue previous metric or add as new one
                    current_metrics.append(line)
                
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
            if current_metrics:
                current_blueprint['success_metrics'] = current_metrics
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
        markdown_output = "# High-Impact Strategic Initiatives\n\n"
        
        if not blueprints:
            markdown_output += "No high-impact initiatives identified.\n"
        else:
            markdown_output += f"## Strategic Implementation Roadmap\n\n"
            markdown_output += f"This comprehensive roadmap outlines {len(blueprints)} strategic initiatives designed to address high-priority actions across all time horizons.\n\n"
            
            for i, blueprint in enumerate(blueprints, 1):
                time_horizon = blueprint.get('time_horizon', 'Not specified')
                markdown_output += f"## {time_horizon} Initiative: {blueprint.get('title', 'Untitled Initiative')}\n\n"
                markdown_output += f"**Time Horizon:** {time_horizon}\n\n"
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
                
                if i < len(blueprints):  # Don't add separator after last item
                    markdown_output += "---\n\n"

        return {
            "status": "success",
            "data": {
                "execution_ready_initiatives": blueprints,
                "formatted_output": markdown_output,
                "raw_llm_response": response
            }
        } 