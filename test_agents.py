import asyncio
import json
from app.agents.best_practices_agent import BestPracticesAgent
from app.agents.scenario_planning_agent import ScenarioPlanningAgent
from app.agents.horizon_scan_agent import HorizonScanAgent
from app.agents.synthesis_agent import SynthesisAgent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agents():
    # Test data
    input_data = {
        'strategic_question': 'What are the market dynamics and growth potential for Electric Vehicles (EVs) in Africa from 2025 to 2040?',
        'problem_analysis': {
            'data': {
                'problem_statement': 'The core problem is to understand the market dynamics, growth potential, and key factors influencing the electric vehicle (EV) market in Africa from 2025 to 2040. This includes assessing market size, consumer behavior, regulatory environment, infrastructure development, and competitive landscape.'
            }
        },
        'time_frame': '2025-2040',
        'region': 'Africa'
    }
    
    # Initialize agents
    agents = {
        'Best Practices': BestPracticesAgent(),
        'Scenario Planning': ScenarioPlanningAgent(),
        'Horizon Scan': HorizonScanAgent(),
        'Synthesis': SynthesisAgent()
    }
    
    # Run each agent
    results = {}
    for name, agent in agents.items():
        try:
            print(f"\n{'='*80}\nRunning {name} Agent\n{'='*80}")
            result = await agent.process(input_data)
            results[name] = result
            
            # Print the full result
            print(f"\n{name} Agent Output:")
            if result.get('status') == 'success':
                print(json.dumps(result['data'], indent=2))
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"\n{'='*80}\n")
            
        except Exception as e:
            logger.error(f"Error running {name} agent: {str(e)}")
            results[name] = {
                'status': 'error',
                'error': str(e),
                'agent_type': name
            }
            print(f"Error running {name} agent: {str(e)}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_agents()) 