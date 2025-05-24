from typing import Dict, Any, List
from .base_agent import BaseAgent
import logging
import json

logger = logging.getLogger(__name__)

class HorizonScanAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are the Horizon Scan Agent. Identify emerging trends and key signals for EV market development in Africa. For each trend and signal, provide:
1. A clear title
2. A description
3. Impact assessment
4. Confidence level (for trends) or relevance and timeframe (for signals)

Format your response exactly like this:
**Emerging Trends:**

1. **[Trend Title]**
   Description: [2-3 sentences]
   Impact: [1-2 sentences]
   Confidence: [High/Medium/Low]

2. **[Trend Title]**
   ...

**Key Signals:**

1. **[Signal Title]**
   Description: [2-3 sentences]
   Relevance: [1-2 sentences]
   Timeframe: [Specific years]"""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        strategic_question = input_data.get('strategic_question', 'N/A')
        problem_statement = input_data.get('problem_analysis', {}).get('data', {}).get('problem_statement', 'N/A')
        
        return f"""Identify emerging trends and key signals for EV market development in Africa (2025-2040).

Strategic Question: {strategic_question}
Problem Context: {problem_statement}

Provide 3-4 emerging trends and 3-4 key signals that could impact the EV market."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = self.format_prompt(input_data)
            response = await self.invoke_llm(prompt)
            
            # Log the raw response for debugging
            logger.info(f"Raw LLM Response:\n{response}")
            
            # Parse the response into structured format
            trends = []
            signals = []
            current_item = None
            current_section = None
            current_field = None
            
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Section headers
                if line.startswith('**Emerging Trends:**'):
                    current_section = 'trends'
                    continue
                elif line.startswith('**Key Signals:**'):
                    current_section = 'signals'
                    continue
                
                # New trend or signal
                if line.startswith('1. **') or line.startswith('2. **') or line.startswith('3. **') or line.startswith('4. **'):
                    if current_item:
                        if current_section == 'trends':
                            trends.append(current_item)
                        else:
                            signals.append(current_item)
                    
                    # Extract title, removing markdown formatting
                    title = line.split('**', 2)[1].strip()
                    
                    current_item = {
                        'name': title,
                        'description': '',
                        'impact': '',
                        'confidence': '',
                        'relevance': '',
                        'timeframe': ''
                    }
                    current_field = None
                
                # Fields
                elif line.startswith('Description:'):
                    current_field = 'description'
                    current_item['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('Impact:'):
                    current_field = 'impact'
                    current_item['impact'] = line.split(':', 1)[1].strip()
                elif line.startswith('Confidence:'):
                    current_field = 'confidence'
                    current_item['confidence'] = line.split(':', 1)[1].strip()
                elif line.startswith('Relevance:'):
                    current_field = 'relevance'
                    current_item['relevance'] = line.split(':', 1)[1].strip()
                elif line.startswith('Timeframe:'):
                    current_field = 'timeframe'
                    current_item['timeframe'] = line.split(':', 1)[1].strip()
                elif current_field and current_item:
                    # Append to current field if it's a continuation
                    current_item[current_field] += ' ' + line
            
            # Add the last item if exists
            if current_item:
                if current_section == 'trends':
                    trends.append(current_item)
                else:
                    signals.append(current_item)
            
            # If no structured items found, create fallbacks
            if not trends:
                trends = [{
                    'name': 'General Trend',
                    'description': response.strip(),
                    'impact': 'N/A',
                    'confidence': 'N/A'
                }]
            
            if not signals:
                signals = [{
                    'name': 'General Signal',
                    'description': response.strip(),
                    'relevance': 'N/A',
                    'timeframe': 'N/A'
                }]
            
            # Log the structured output for verification
            logger.info(f"Structured Output:\n{json.dumps({'trends': trends, 'signals': signals}, indent=2)}")
            
            return self.format_output({
                "emerging_trends": trends,
                "key_signals": signals
            })
            
        except Exception as e:
            logger.error(f"Error in HorizonScanAgent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            } 