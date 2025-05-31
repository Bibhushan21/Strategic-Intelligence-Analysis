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
        # Initialize agents in the desired order
        self.agents = {
            "Problem Explorer": ProblemExplorerAgent(),
            "Best Practices": BestPracticesAgent(),
            "Horizon Scanning": HorizonScanningAgent(),
            "Scenario Planning": ScenarioPlanningAgent(),
            "Research Synthesis": ResearchSynthesisAgent(),
            "Strategic Action": StrategicActionAgent(),
            "High Impact": HighImpactAgent(),
            "Backcasting": BackcastingAgent()
        }
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
Additional Instructions: {input_data.get('prompt', 'N/A')}

Previous Analysis Results:
{self._format_previous_results(input_data)}

Provide a coordinated analysis plan and execution strategy."""

    def _format_previous_results(self, input_data: Dict[str, Any]) -> str:
        """Format previous analysis results for the prompt"""
        results = []
        for agent_type in ['problem_explorer', 'best_practices', 'horizon_scanning', 
                          'scenario_planning', 'research_synthesis', 'strategic_action', 'high_impact']:
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
                    timeout=60  # Increased timeout to 60 seconds
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
                    # Return a dictionary indicating error, to be handled by the main process method
                    return {
                        "status": "error",
                        "error": f"Agent {agent_name} timed out after {self.max_retries} retries. Please try again with a simpler prompt.",
                        "agent_type": agent_name  # Or agent.__class__.__name__
                    }
                delay = self.base_delay * (2 ** retries)  # Exponential backoff
                await asyncio.sleep(delay)
                
            except HTTPException as he:
                if he.status_code == 429:  # Rate limit exceeded
                    retries += 1
                    if retries == self.max_retries:
                        # Return a dictionary indicating error, to be handled by the main process method
                        return {
                            "status": "error",
                            "error": f"Rate limit exceeded for {agent_name} after {self.max_retries} retries. Please try again in a few minutes.",
                            "agent_type": agent_name
                        }
                    delay = self.base_delay * (2 ** retries)  # Exponential backoff
                    await asyncio.sleep(delay)
                else:
                    raise he
                    
            except Exception as e:
                logger.error(f"Error in {agent_name}: {str(e)}")
                retries += 1
                if retries == self.max_retries:
                    # Return a dictionary indicating error, to be handled by the main process method
                    return {
                        "status": "error",
                        "error": f"Agent {agent_name} failed after {self.max_retries} retries: {str(e)}",
                        "agent_type": agent_name  # Or agent.__class__.__name__
                    }
                delay = self.base_delay * (2 ** retries)
                await asyncio.sleep(delay)
        # Should not be reached if max_retries is effective, but as a fallback:
        return {
            "status": "error",
            "error": f"Agent {agent_name} failed due to an unexpected issue after retries.",
            "agent_type": agent_name
        }

    async def process(self, initial_input_data: Dict[str, Any]) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        # Make a mutable copy for accumulating results that feed into subsequent agents
        cumulative_input_data = initial_input_data.copy()

        # Define a map for agent display names to their keys in input_data
        agent_names_map = {
            "Problem Explorer": "problem_explorer",
            "Best Practices": "best_practices",
            "Horizon Scanning": "horizon_scanning",
            "Scenario Planning": "scenario_planning",
            "Research Synthesis": "research_synthesis",
            "Strategic Action": "strategic_action",
            "High Impact": "high_impact",
            "Backcasting": "backcasting"
        }

        # Helper to process an agent and handle its result
        async def run_agent(agent_name: str, current_input_data: Dict[str, Any]):
            agent_key = agent_names_map[agent_name]
            agent_instance = self.agents[agent_name]
            
            logger.info(f"\nStarting {agent_name}...")
            result = await self.rate_limited_process(agent_instance, current_input_data.copy(), agent_name) # Pass a copy
            
            if result.get("status") == "error":
                logger.error(f"Error in {agent_name}: {result.get('error', 'Unknown error')}")
                # Propagate the error result, it will be checked by the caller
                results[agent_name] = result 
                raise HTTPException(status_code=500, detail=f"Error in {agent_name}: {result.get('error', 'Unknown error')}")

            results[agent_name] = result
            cumulative_input_data[agent_key] = result
            logger.info(f"{agent_name} completed successfully.")
            return result

        try:
            # --- Stage 1: Problem Explorer ---
            await run_agent("Problem Explorer", cumulative_input_data)

            # --- Stage 2: Best Practices, Horizon Scanning, Scenario Planning (Parallel) ---
            agent_bp_name = "Best Practices"
            agent_hs_name = "Horizon Scanning"
            agent_sp_name = "Scenario Planning"

            # Tasks for parallel execution
            # They all use cumulative_input_data which now includes problem_explorer output
            input_for_stage2 = cumulative_input_data.copy() 

            bp_task = self.rate_limited_process(self.agents[agent_bp_name], input_for_stage2, agent_bp_name)
            hs_task = self.rate_limited_process(self.agents[agent_hs_name], input_for_stage2, agent_hs_name)
            sp_task = self.rate_limited_process(self.agents[agent_sp_name], input_for_stage2, agent_sp_name)
            
            logger.info("\nStarting parallel execution of Best Practices, Horizon Scanning, Scenario Planning...")
            stage2_results_list = await asyncio.gather(bp_task, hs_task, sp_task, return_exceptions=True)
            
            # Process results from asyncio.gather
            parallel_agent_names = [agent_bp_name, agent_hs_name, agent_sp_name]
            for i, result_or_exc in enumerate(stage2_results_list):
                agent_name = parallel_agent_names[i]
                agent_key = agent_names_map[agent_name]

                if isinstance(result_or_exc, Exception):
                    logger.error(f"Exception in parallel agent {agent_name}: {str(result_or_exc)}")
                    results[agent_name] = {"status": "error", "error": str(result_or_exc), "agent_type": agent_name}
                    raise HTTPException(status_code=500, detail=f"Error in {agent_name} (parallel stage): {str(result_or_exc)}")
                
                result = result_or_exc
                if result.get("status") == "error":
                    logger.error(f"Error in parallel agent {agent_name}: {result.get('error', 'Unknown error')}")
                    results[agent_name] = result
                    raise HTTPException(status_code=500, detail=f"Error in {agent_name} (parallel stage): {result.get('error', 'Unknown error')}")

                results[agent_name] = result
                cumulative_input_data[agent_key] = result
                logger.info(f"Parallel agent {agent_name} completed successfully.")

            # --- Stage 3: Research Synthesis ---
            await run_agent("Research Synthesis", cumulative_input_data)
            
            # --- Stage 4: Strategic Action ---
            await run_agent("Strategic Action", cumulative_input_data)

            # --- Stage 5: High Impact ---
            await run_agent("High Impact", cumulative_input_data)

            # --- Stage 6: Backcasting ---
            # For Backcasting, we run it but don't strictly need to add its output to cumulative_input_data
            # if no other agent consumes it from there. Results dict is the final output.
            agent_bc_name = "Backcasting"
            agent_bc = self.agents[agent_bc_name]
            logger.info(f"\nStarting {agent_bc_name}...")
            bc_result = await self.rate_limited_process(agent_bc, cumulative_input_data.copy(), agent_bc_name)
            if bc_result.get("status") == "error":
                logger.error(f"Error in {agent_bc_name}: {bc_result.get('error', 'Unknown error')}")
                results[agent_bc_name] = bc_result
                raise HTTPException(status_code=500, detail=f"Error in {agent_bc_name}: {bc_result.get('error', 'Unknown error')}")
            results[agent_bc_name] = bc_result
            logger.info(f"{agent_bc_name} completed successfully.")

        except HTTPException as he:
            logger.error(f"Orchestrator caught HTTPException: {he.detail}")
            # Ensure a consistent error structure if an agent fails mid-process
            # The 'results' dictionary might be partially filled.
            # The HTTPException will be propagated up by FastAPI.
            # We could add more details to the 'results' if needed here.
            return {
                "status": "error",
                "error_detail": he.detail,
                "completed_stages_results": results # Return what was completed
            }
        except Exception as e:
            logger.error(f"Unexpected error in OrchestratorAgent.process: {str(e)}")
            return {
                "status": "error",
                "error_detail": f"Orchestrator failed: {str(e)}",
                "completed_stages_results": results
            } 
            
        return results 