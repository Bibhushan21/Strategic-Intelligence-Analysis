from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import json


logger = logging.getLogger(__name__)


class ResearchSynthesisAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Research Synthesis Agent. Your mission is to synthesize insights from various analysis components into a coherent strategic narrative. Focus on:


1. Pattern Recognition: Identify common themes and patterns across analyses
2. Insight Integration: Combine findings from different perspectives
3. Strategic Implications: Extract key strategic implications
4. Actionable Insights: Highlight actionable recommendations
5. Knowledge Gaps: Identify areas needing further investigation


Your role is to create a comprehensive synthesis that brings together all analysis components."""


    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        problem_statement = input_data.get('problem_analysis', {}).get('data', {}).get('problem_statement', 'N/A')
        best_practices = input_data.get('best_practices', {}).get('data', {}).get('practices', [])
        horizon_scan = input_data.get('horizon_scan', {}).get('data', {}).get('raw_sections', {})
        scenarios = input_data.get('scenarios', {}).get('data', {}).get('scenarios', [])


        # Format best practices
        best_practices_text = "\n".join([f"- {p['title']}: {p['description']}" for p in best_practices[:2]]) if best_practices else "N/A"
       
        # Format horizon scan
        horizon_scan_text = ""
        if horizon_scan:
            if 'weak_signals' in horizon_scan:
                horizon_scan_text += "Key Weak Signals:\n"
                for signal in horizon_scan['weak_signals'][:2]:
                    horizon_scan_text += f"- {signal['title']}: {signal['description']}\n"
           
            if 'key_uncertainties' in horizon_scan:
                horizon_scan_text += "\nKey Uncertainties:\n"
                for uncertainty in horizon_scan['key_uncertainties'][:2]:
                    horizon_scan_text += f"- {uncertainty['title']}: {uncertainty['description']}\n"
           
            if 'change_drivers' in horizon_scan:
                horizon_scan_text += "\nKey Change Drivers:\n"
                for category, drivers in horizon_scan['change_drivers'].items():
                    if drivers:
                        horizon_scan_text += f"- {category.title()}: {', '.join(drivers[:2])}\n"
       
        # Format scenarios
        scenarios_text = "\n".join([f"- {s.get('name', 'N/A')}: {s.get('description', 'N/A')}" for s in scenarios[:2]]) if scenarios else "N/A"


        return f"""Synthesize the following research findings for the strategic question: {input_data.get('strategic_question', 'N/A')}


Problem Definition: {problem_statement}


Key Best Practices:
{best_practices_text}


Key Horizon Scan Insights:
{horizon_scan_text}


Key Scenarios:
{scenarios_text}


Additional Instructions: {input_data.get('prompt', 'N/A')}


Provide a concise synthesis focusing on overarching insights and strategic implications."""


    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
           
            # Log the raw response for debugging
            logger.info(f"Raw LLM Response:\n{response}")
           
            # Parse the response into structured format
            sections = {
                "key_insights": [],
                "strategic_implications": [],
                "actionable_recommendations": [],
                "knowledge_gaps": []
            }
           
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
               
                if "Key Insights" in line:
                    current_section = "key_insights"
                    continue
                elif "Strategic Implications" in line:
                    current_section = "strategic_implications"
                    continue
                elif "Actionable Recommendations" in line:
                    current_section = "actionable_recommendations"
                    continue
                elif "Knowledge Gaps" in line:
                    current_section = "knowledge_gaps"
                    continue
               
                if current_section and (line.startswith("- ") or line.startswith("* ")):
                    sections[current_section].append(line[2:].strip())
                elif current_section and sections[current_section]:
                    sections[current_section][-1] += " " + line
           
            # Log the structured output for verification
            logger.info(f"Structured Output:\n{json.dumps(sections, indent=2)}")
           
            return self.format_output(sections)
           
        except Exception as e:
            logger.error(f"Error in ResearchSynthesisAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }


    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        try:
            # Create a human-readable markdown format
            markdown_output = "# Research Synthesis\n\n"
            
            # Key Insights
            if data.get('key_insights'):
                markdown_output += "## Key Insights\n\n"
                for insight in data['key_insights']:
                    markdown_output += f"- {insight}\n"
                markdown_output += "\n"
            
            # Strategic Implications
            if data.get('strategic_implications'):
                markdown_output += "## Strategic Implications\n\n"
                for implication in data['strategic_implications']:
                    markdown_output += f"- {implication}\n"
                markdown_output += "\n"
            
            # Actionable Recommendations
            if data.get('actionable_recommendations'):
                markdown_output += "## Actionable Recommendations\n\n"
                for recommendation in data['actionable_recommendations']:
                    markdown_output += f"- {recommendation}\n"
                markdown_output += "\n"
            
            # Knowledge Gaps
            if data.get('knowledge_gaps'):
                markdown_output += "## Knowledge Gaps\n\n"
                for gap in data['knowledge_gaps']:
                    markdown_output += f"- {gap}\n"
                markdown_output += "\n"
            
            # Log the formatted output
            logger.info(f"Formatted Output:\n{markdown_output}")
            
            return {
                "status": "success",
                "data": {
                    "raw_sections": data,
                    "formatted_output": markdown_output,
                    "raw_response": markdown_output  # Add raw_response for frontend compatibility
                }
            }
        except Exception as e:
            logger.error(f"Error formatting output: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "data": {
                    "formatted_output": f"# Research Synthesis\n\nError: {str(e)}",
                    "raw_response": f"# Research Synthesis\n\nError: {str(e)}"
                }
            }
