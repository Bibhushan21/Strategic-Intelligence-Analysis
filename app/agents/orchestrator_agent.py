from typing import Dict, Any, List
from .base_agent import BaseAgent
from .problem_explorer_agent import ProblemExplorerAgent
from .best_practices_agent import BestPracticesAgent
from .horizon_scanning_agent import HorizonScanningAgent
from .scenario_planning_agent import ScenarioPlanningAgent
from .research_synthesis_agent import ResearchSynthesisAgent
from .strategic_action_agent import StrategicActionAgent
from .high_impact_agent import HighImpactAgent
from .backcasting_agent import BackcastingAgent
import asyncio
import time
from fastapi import HTTPException
import random
import logging
import json

logger = logging.getLogger(__name__)

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # Initialize all agents
        self.problem_explorer = ProblemExplorerAgent()
        self.best_practices = BestPracticesAgent()
        self.horizon_scanning = HorizonScanningAgent()
        self.scenario_planning = ScenarioPlanningAgent()
        self.research_synthesis = ResearchSynthesisAgent()
        self.strategic_action = StrategicActionAgent()
        self.high_impact = HighImpactAgent()
        self.backcasting = BackcastingAgent()
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Minimum time between requests in seconds
        self.max_retries = 3
        self.base_delay = 1.0  # Base delay for exponential backoff

    def get_system_prompt(self) -> str:
        return """You are the Orchestrator Agent. Your mission is to coordinate and manage the strategic intelligence analysis process. Focus on:

1. Task Coordination: Manage the flow of analysis between agents
2. Data Integration: Combine insights from different agents
3. Quality Control: Ensure analysis quality and consistency
4. Progress Tracking: Monitor analysis progress
5. Result Synthesis: Integrate final results

Your role is to ensure a smooth and effective analysis process."""

    def format_prompt(self, input_data: Dict[str, Any]) -> str:
        return f"""Coordinate the analysis of the following strategic challenge:

Strategic Question: {input_data.get('strategic_question', 'N/A')}
Time Frame: {input_data.get('time_frame', 'N/A')}
Region: {input_data.get('region', 'N/A')}
Scope: {', '.join(input_data.get('scope', []))}
Additional Instructions: {input_data.get('prompt', 'N/A')}

Previous Analysis Results:
{self._format_previous_results(input_data)}

Provide a coordinated analysis plan and execution strategy."""

    def _format_previous_results(self, input_data: Dict[str, Any]) -> str:
        """Format previous analysis results for the prompt"""
        results = []
        for agent_type in ['problem_analysis', 'best_practices', 'horizon_scan', 
                          'scenarios', 'synthesis', 'action_plan', 'high_impact']:
            if agent_type in input_data:
                results.append(f"{agent_type.replace('_', ' ').title()}: {input_data[agent_type].get('data', {})}")
        return '\n'.join(results) if results else 'No previous results available'

    async def rate_limited_process(self, agent, input_data: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """
        Process with rate limiting, exponential backoff, and retries.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                current_time = time.time()
                time_since_last_request = current_time - self.last_request_time
                
                if time_since_last_request < self.min_request_interval:
                    await asyncio.sleep(self.min_request_interval - time_since_last_request)
                
                # Add jitter to prevent thundering herd
                jitter = random.uniform(0, 0.1)
                await asyncio.sleep(jitter)
                
                logger.info(f"\nProcessing {agent_name}...")
                logger.info(f"Input data keys: {list(input_data.keys())}")
                
                # Add timeout to the process call
                result = await asyncio.wait_for(
                    agent.process(input_data),
                    timeout=25  # 25 seconds timeout for each agent
                )
                
                # Log the raw LLM response for all agents
                if 'data' in result:
                    logger.info(f"\nRaw LLM Response for {agent_name}:")
                    if isinstance(result['data'], dict):
                        if 'formatted_output' in result['data']:
                            logger.info("\nFormatted Output:")
                            logger.info(result['data']['formatted_output'])
                        if 'raw_sections' in result['data']:
                            logger.info("\nRaw Sections:")
                            logger.info(json.dumps(result['data']['raw_sections'], indent=2))
                    else:
                        logger.info(json.dumps(result['data'], indent=2))
                
                logger.info(f"\n{agent_name} completed with status: {result.get('status', 'unknown')}")
                self.last_request_time = time.time()
                return result
                
            except asyncio.TimeoutError:
                retries += 1
                if retries == self.max_retries:
                    raise HTTPException(
                        status_code=504,
                        detail=f"Agent {agent_name} timed out after {self.max_retries} retries. Please try again with a simpler prompt."
                    )
                delay = self.base_delay * (2 ** retries)  # Exponential backoff
                await asyncio.sleep(delay)
                
            except HTTPException as he:
                if he.status_code == 429:  # Rate limit exceeded
                    retries += 1
                    if retries == self.max_retries:
                        raise HTTPException(
                            status_code=429,
                            detail=f"Rate limit exceeded for {agent_name} after {self.max_retries} retries. Please try again in a few minutes."
                        )
                    delay = self.base_delay * (2 ** retries)  # Exponential backoff
                    await asyncio.sleep(delay)
                else:
                    raise he
                    
            except Exception as e:
                logger.error(f"Error in {agent_name}: {str(e)}")
                retries += 1
                if retries == self.max_retries:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error in {agent_name}: {str(e)}"
                    )
                delay = self.base_delay * (2 ** retries)
                await asyncio.sleep(delay)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the entire analysis workflow with sequential processing to avoid rate limits.
        """
        try:
            logger.info("\nStarting analysis workflow...")
            
            # Phase 1: Initial Analysis
            logger.info("\nPhase 1: Problem Analysis")
            problem_frame = await self.rate_limited_process(self.problem_explorer, input_data, "Problem Explorer")
            if problem_frame.get('status') != 'success':
                raise Exception(f"Problem Explorer failed: {problem_frame.get('error', 'Unknown error')}")
            
            # Update input data with problem frame
            input_data['problem_analysis'] = problem_frame
            
            # Phase 2: Best Practices and Horizon Scanning
            logger.info("\nPhase 2: Best Practices and Horizon Scanning")
            best_practices = await self.rate_limited_process(self.best_practices, input_data, "Best Practices")
            if best_practices.get('status') != 'success':
                raise Exception(f"Best Practices failed: {best_practices.get('error', 'Unknown error')}")
                
            horizon_scan = await self.rate_limited_process(self.horizon_scanning, input_data, "Horizon Scanning")
            if horizon_scan.get('status') != 'success':
                raise Exception(f"Horizon Scanning failed: {horizon_scan.get('error', 'Unknown error')}")
            
            # Update input data with new results
            input_data['best_practices'] = best_practices
            input_data['horizon_scan'] = horizon_scan

            # Phase 3: Scenario Development
            logger.info("\nPhase 3: Scenario Development")
            scenarios = await self.rate_limited_process(
                self.scenario_planning,
                input_data,
                "Scenario Planning"
            )
            if scenarios.get('status') != 'success':
                raise Exception(f"Scenario Planning failed: {scenarios.get('error', 'Unknown error')}")
            input_data['scenarios'] = scenarios

            # Phase 4: Research Synthesis
            logger.info("\nPhase 4: Research Synthesis")
            synthesis = await self.rate_limited_process(
                self.research_synthesis,
                input_data,
                "Research Synthesis"
            )
            if synthesis.get('status') != 'success':
                raise Exception(f"Research Synthesis failed: {synthesis.get('error', 'Unknown error')}")
            input_data['synthesis'] = synthesis

            # Phase 5: Action Planning
            logger.info("\nPhase 5: Action Planning")
            action_plan = await self.rate_limited_process(
                self.strategic_action,
                input_data,
                "Strategic Action"
            )
            if action_plan.get('status') != 'success':
                raise Exception(f"Strategic Action failed: {action_plan.get('error', 'Unknown error')}")
            input_data['action_plan'] = action_plan

            # Phase 6: High-Impact Initiatives
            logger.info("\nPhase 6: High-Impact Initiatives")
            initiatives = await self.rate_limited_process(
                self.high_impact,
                input_data,
                "High Impact"
            )
            if initiatives.get('status') != 'success':
                raise Exception(f"High Impact failed: {initiatives.get('error', 'Unknown error')}")
            input_data['initiatives'] = initiatives

            # Phase 7: Backcasting
            logger.info("\nPhase 7: Backcasting")
            prioritized_tasks = await self.rate_limited_process(
                self.backcasting,
                input_data,
                "Backcasting"
            )
            if prioritized_tasks.get('status') != 'success':
                raise Exception(f"Backcasting failed: {prioritized_tasks.get('error', 'Unknown error')}")

            logger.info("\nAnalysis workflow completed successfully!")
            
            # Return comprehensive results
            return {
                "status": "success",
                "data": {
                    "problem_analysis": problem_frame,
                    "best_practices": best_practices,
                    "horizon_scan": horizon_scan,
                    "scenarios": scenarios,
                    "synthesis": synthesis,
                    "action_plan": action_plan,
                    "initiatives": initiatives,
                    "prioritized_tasks": prioritized_tasks
                }
            }

        except HTTPException as he:
            logger.error(f"HTTP Exception: {he.detail}")
            return {
                "status": "error",
                "error": he.detail,
                "agent_type": self.__class__.__name__
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_type": self.__class__.__name__
            } 