from typing import Dict, Any
from .base_agent import BaseAgent

class ProblemExplorerAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Problem Explorer Agent. Your mission is to analyze and deconstruct strategic challenges. Focus on:

1. Problem Definition: Clearly define the core problem.
2. Key Questions: Identify 2-3 critical questions to address.
3. Information Gaps: List 2-3 key information gaps.
4. Initial Hypothesis: Formulate 1-2 initial hypotheses.

Keep your analysis concise and focused on actionable insights."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        return f"""Analyze the following strategic challenge:

Strategic Question: {input_data.get('strategic_question', 'N/A')}
Time Frame: {input_data.get('time_frame', 'N/A')}
Region: {input_data.get('region', 'N/A')}
Scope: {', '.join(input_data.get('scope', []))}
Additional Instructions: {input_data.get('prompt', 'N/A')}

Provide a structured problem analysis."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Parse the response into structured sections
            sections = {
                "problem_statement": "",
                "key_questions": [],
                "information_gaps": [],
                "initial_hypotheses": []
            }
            
            current_section = None
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if "Problem Definition" in line:
                    current_section = "problem_statement"
                elif "Key Questions" in line:
                    current_section = "key_questions"
                elif "Information Gaps" in line:
                    current_section = "information_gaps"
                elif "Initial Hypothesis" in line:
                    current_section = "initial_hypotheses"
                elif current_section:
                    if current_section == "problem_statement":
                        sections[current_section] += line + " "
                    else:
                        if line.startswith("- ") or line.startswith("* "):
                            sections[current_section].append(line[2:])
                        else:
                            sections[current_section].append(line)
            
            # Clean up problem statement
            sections["problem_statement"] = sections["problem_statement"].strip()

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
        markdown_output = f"""# Problem Analysis

## Problem Definition
{sections['problem_statement']}

## Key Questions
{chr(10).join(f"- {q}" for q in sections['key_questions'])}

## Information Gaps
{chr(10).join(f"- {gap}" for gap in sections['information_gaps'])}

## Initial Hypotheses
{chr(10).join(f"- {hyp}" for hyp in sections['initial_hypotheses'])}
"""

        return {
            "status": "success",
            "data": {
                "raw_sections": sections,
                "formatted_output": markdown_output
            }
        } 