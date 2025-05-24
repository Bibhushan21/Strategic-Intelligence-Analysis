from typing import Dict, Any
from .base_agent import BaseAgent

class ResearchSynthesisAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Research Synthesis Agent. Your mission is to integrate findings from previous analyses to identify overarching insights. Focus on:

1. Key Insights: Identify 2-3 main themes or patterns emerging from all analyses.
2. Market Analysis: Analyze the current market conditions and trends.
3. Strategic Implications: Note 1-2 significant strategic implications for the organization.
4. Recommendations: Provide 2-3 actionable recommendations based on the synthesis.

Format your response exactly like this:

Key Insights:
- [Insight 1]
- [Insight 2]
- [Insight 3]

Market Analysis:
- [Analysis point 1]
- [Analysis point 2]

Strategic Implications:
- [Implication 1]
- [Implication 2]

Recommendations:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]

Keep your synthesis concise and high-level."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        problem_statement = input_data.get('problem_analysis', {}).get('data', {}).get('problem_statement', 'N/A')
        best_practices = input_data.get('best_practices', {}).get('data', {}).get('practices', [])
        horizon_trends = input_data.get('horizon_scan', {}).get('data', {}).get('emerging_trends', [])
        scenarios = input_data.get('scenarios', {}).get('data', {}).get('scenarios', [])

        # Format best practices
        best_practices_text = "\n".join([f"- {p['title']}: {p['description']}" for p in best_practices[:2]]) if best_practices else "N/A"
        
        # Format horizon trends
        horizon_trends_text = "\n".join([f"- {trend}" for trend in horizon_trends[:2]]) if horizon_trends else "N/A"
        
        # Format scenarios
        scenarios_text = "\n".join([f"- {s.get('name', 'N/A')}: {s.get('description', 'N/A')}" for s in scenarios[:2]]) if scenarios else "N/A"

        return f"""Synthesize the following research findings for the strategic question: {input_data.get('strategic_question', 'N/A')}

Problem Definition: {problem_statement}

Key Best Practices:
{best_practices_text}

Key Horizon Trends:
{horizon_trends_text}

Key Scenarios:
{scenarios_text}

Additional Instructions: {input_data.get('prompt', 'N/A')}

Provide a concise synthesis focusing on overarching insights and strategic implications."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Parse the response into sections
            sections = {
                "key_insights": [],
                "market_analysis": [],
                "strategic_implications": [],
                "recommendations": []
            }
            
            current_section = None
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if "Key Insights:" in line or "Key Insights" in line:
                    current_section = "key_insights"
                    continue
                elif "Market Analysis:" in line or "Market Analysis" in line:
                    current_section = "market_analysis"
                    continue
                elif "Strategic Implications:" in line or "Strategic Implications" in line:
                    current_section = "strategic_implications"
                    continue
                elif "Recommendations:" in line or "Recommendations" in line:
                    current_section = "recommendations"
                    continue
                
                # Add content to current section
                if current_section and (line.startswith('- ') or line.startswith('* ')):
                    sections[current_section].append(line[2:].strip())
                elif current_section:
                    # Handle multi-line content
                    if sections[current_section]:
                        sections[current_section][-1] += " " + line
                    else:
                        sections[current_section].append(line)
            
            # Ensure no empty sections
            for section in sections:
                if not sections[section]:
                    sections[section] = ["No specific insights available"]
            
            return self.format_output(sections)
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            }

    def format_output(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output in a structured way."""
        # Create a human-readable markdown format
        markdown_output = f"""# Research Synthesis

## Key Insights
{chr(10).join(f"- {insight}" for insight in sections['key_insights'])}

## Market Analysis
{chr(10).join(f"- {analysis}" for analysis in sections['market_analysis'])}

## Strategic Implications
{chr(10).join(f"- {implication}" for implication in sections['strategic_implications'])}

## Recommendations
{chr(10).join(f"- {recommendation}" for recommendation in sections['recommendations'])}
"""

        return {
            "status": "success",
            "data": {
                "raw_sections": sections,
                "formatted_output": markdown_output
            }
        } 