from typing import Dict, Any, List, Optional
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

# Database imports - Fixed path handling
import sys
import os
from pathlib import Path

# Get the project root directory (Strategic Intelligence App)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # Go up from agents -> app -> project root
data_path = project_root / 'data'

# Add data directory to Python path
sys.path.insert(0, str(data_path))

# Database imports
try:
    from database_service import DatabaseService
    from database_config import test_connection
    DATABASE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Database modules not available: {e}")
    DATABASE_AVAILABLE = False

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
        
        # Database session tracking
        self.current_session_id = None
        self.session_start_time = None
        self.db_enabled = self._test_database_connection()

    def _test_database_connection(self) -> bool:
        """Test if database is available."""
        if not DATABASE_AVAILABLE:
            logger.warning("Database modules not available - running without database storage")
            return False
            
        try:
            if test_connection():
                logger.info("Database connection successful - enabling database features")
                return True
            else:
                logger.warning("Database connection failed - running without database storage")
                return False
        except Exception as e:
            logger.warning(f"Database connection test failed: {str(e)} - running without database storage")
            return False

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

    def _create_analysis_session(self, input_data: Dict[str, Any]) -> None:
        """Create database session for the analysis."""
        if not self.db_enabled or not DATABASE_AVAILABLE:
            return
            
        try:
            self.current_session_id = DatabaseService.create_analysis_session(
                strategic_question=input_data.get('strategic_question', ''),
                time_frame=input_data.get('time_frame', ''),
                region=input_data.get('region', ''),
                additional_instructions=input_data.get('prompt', ''),
                user_id=input_data.get('user_id')
            )
            self.session_start_time = time.time()
            
            if self.current_session_id:
                # Minimal logging - just session creation
                print(f"Created database session {self.current_session_id}")
                # Log session creation
                DatabaseService.log_system_event(
                    log_level="INFO",
                    component="orchestrator",
                    message=f"Analysis session {self.current_session_id} started",
                    session_id=self.current_session_id,
                    details={
                        "strategic_question": input_data.get('strategic_question', ''),
                        "time_frame": input_data.get('time_frame', ''),
                        "region": input_data.get('region', '')
                    }
                )
            else:
                print("Failed to create database session")
                
        except Exception as e:
            print(f"Error creating database session: {str(e)}")
            self.current_session_id = None

    def _save_agent_result(self, agent_name: str, result: Dict[str, Any], processing_time: float) -> Optional[int]:
        """Save individual agent result to database and return the result ID."""
        if not self.db_enabled or not self.current_session_id or not DATABASE_AVAILABLE:
            return None
            
        try:
            # Extract different data formats from result
            raw_response = ""
            formatted_output = ""
            structured_data = {}
            
            if isinstance(result.get('data'), dict):
                # Get raw response (could be the full data or a specific field)
                raw_response = json.dumps(result['data'], indent=2)
                
                # Get formatted output (markdown content)
                if 'formatted_output' in result['data']:
                    formatted_output = result['data']['formatted_output']
                elif 'analysis' in result['data']:
                    formatted_output = result['data']['analysis']
                else:
                    formatted_output = str(result['data'])
                
                # Store structured data
                structured_data = result['data']
            else:
                raw_response = str(result.get('data', ''))
                formatted_output = raw_response
                structured_data = result
            
            # Determine agent type
            agent_type_map = {
                "Problem Explorer": "analysis",
                "Best Practices": "research", 
                "Horizon Scanning": "scanning",
                "Scenario Planning": "planning",
                "Research Synthesis": "synthesis",
                "Strategic Action": "strategy",
                "High Impact": "impact",
                "Backcasting": "backcasting"
            }
            
            agent_type = agent_type_map.get(agent_name, "general")
            status = "completed" if result.get('status') != 'error' else "failed"
            
            result_id = DatabaseService.save_agent_result(
                session_id=self.current_session_id,
                agent_name=agent_name,
                agent_type=agent_type,
                raw_response=raw_response,
                formatted_output=formatted_output,
                structured_data=structured_data,
                processing_time=processing_time,
                status=status
            )
            
            if result_id:
                print(f"Saved result for agent {agent_name} in session {self.current_session_id}")
                print(f"Saved {agent_name} result to database (ID: {result_id})")
                # Add database IDs to the result so they can be passed to frontend
                result['agent_result_id'] = result_id
                result['session_id'] = self.current_session_id
                return result_id
            else:
                print(f"Failed to save result for agent {agent_name}")
                return None
                
        except Exception as e:
            print(f"Error saving agent result to database: {str(e)}")
            return None

    def _update_session_completion(self, status: str = "completed") -> None:
        """Update session completion status and total processing time."""
        if not self.db_enabled or not self.current_session_id or not DATABASE_AVAILABLE:
            return
            
        try:
            total_time = None
            if self.session_start_time:
                total_time = time.time() - self.session_start_time
            
            success = DatabaseService.update_session_status(
                session_id=self.current_session_id,
                status=status,
                total_processing_time=total_time
            )
            
            if success:
                logger.info(f"Updated session {self.current_session_id} status to {status}")
                # Log completion
                DatabaseService.log_system_event(
                    log_level="INFO",
                    component="orchestrator",
                    message=f"Analysis session {self.current_session_id} {status}",
                    session_id=self.current_session_id,
                    details={
                        "total_processing_time": total_time,
                        "status": status
                    }
                )
            else:
                logger.error(f"Failed to update session {self.current_session_id} status")
                
        except Exception as e:
            logger.error(f"Error updating session completion: {str(e)}")

    async def rate_limited_process(self, agent, input_data: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """
        Process with rate limiting, exponential backoff, and retries.
        Now includes database result saving.
        """
        retries = 0
        agent_start_time = time.time()
        
        while retries < self.max_retries:
            try:
                current_time = time.time()
                time_since_last_request = current_time - self.last_request_time
                
                if time_since_last_request < self.min_request_interval:
                    await asyncio.sleep(self.min_request_interval - time_since_last_request)
                
                # Add jitter to prevent thundering herd
                jitter = random.uniform(0, 0.1)
                await asyncio.sleep(jitter)
                
                # Minimal logging - just progress
                print(f"{agent_name} started processing...")
                
                # Add timeout to the process call
                result = await asyncio.wait_for(
                    agent.process(input_data),
                    timeout=60  # Increased timeout to 60 seconds
                )
                
                # Calculate processing time
                processing_time = time.time() - agent_start_time
                
                # Minimal completion logging
                print(f"{agent_name} completed with status: {result.get('status', 'unknown')}")
                
                # Save agent result to database
                self._save_agent_result(agent_name, result, processing_time)
                
                self.last_request_time = time.time()
                return result
                
            except asyncio.TimeoutError:
                retries += 1
                processing_time = time.time() - agent_start_time
                
                if retries == self.max_retries:
                    # Save timeout result to database
                    timeout_result = {
                        "status": "error",
                        "error": f"Agent {agent_name} timed out after {self.max_retries} retries. Please try again with a simpler prompt.",
                        "agent_type": agent_name
                    }
                    self._save_agent_result(agent_name, timeout_result, processing_time)
                    return timeout_result
                    
                delay = self.base_delay * (2 ** retries)  # Exponential backoff
                await asyncio.sleep(delay)
                
            except HTTPException as he:
                processing_time = time.time() - agent_start_time
                
                if he.status_code == 429:  # Rate limit exceeded
                    retries += 1
                    if retries == self.max_retries:
                        rate_limit_result = {
                            "status": "error",
                            "error": f"Rate limit exceeded for {agent_name} after {self.max_retries} retries. Please try again in a few minutes.",
                            "agent_type": agent_name
                        }
                        self._save_agent_result(agent_name, rate_limit_result, processing_time)
                        return rate_limit_result
                        
                    delay = self.base_delay * (2 ** retries)  # Exponential backoff
                    await asyncio.sleep(delay)
                else:
                    # Save error result to database
                    error_result = {
                        "status": "error",
                        "error": f"HTTP error {he.status_code}: {he.detail}",
                        "agent_type": agent_name
                    }
                    self._save_agent_result(agent_name, error_result, processing_time)
                    raise he
                    
            except Exception as e:
                processing_time = time.time() - agent_start_time
                print(f"Error in {agent_name}: {str(e)}")
                retries += 1
                
                if retries == self.max_retries:
                    error_result = {
                        "status": "error",
                        "error": f"Agent {agent_name} failed after {self.max_retries} retries: {str(e)}",
                        "agent_type": agent_name
                    }
                    self._save_agent_result(agent_name, error_result, processing_time)
                    return error_result
                    
                delay = self.base_delay * (2 ** retries)
                await asyncio.sleep(delay)

        # Fallback - should not be reached
        fallback_result = {
            "status": "error",
            "error": f"Agent {agent_name} failed due to an unexpected issue after retries.",
            "agent_type": agent_name
        }
        processing_time = time.time() - agent_start_time
        self._save_agent_result(agent_name, fallback_result, processing_time)
        return fallback_result

    async def process(self, initial_input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Create database session at start
        self._create_analysis_session(initial_input_data)
        
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
            
            result = await self.rate_limited_process(agent_instance, current_input_data.copy(), agent_name) # Pass a copy
            
            if result.get("status") == "error":
                print(f"Error in {agent_name}: {result.get('error', 'Unknown error')}")
                # Propagate the error result, it will be checked by the caller
                results[agent_name] = result 
                # Update session status to failed
                self._update_session_completion("failed")
                raise HTTPException(status_code=500, detail=f"Error in {agent_name}: {result.get('error', 'Unknown error')}")

            results[agent_name] = result
            cumulative_input_data[agent_key] = result
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
            
            stage2_results_list = await asyncio.gather(bp_task, hs_task, sp_task, return_exceptions=True)
                
            # Process results from asyncio.gather
            parallel_agent_names = [agent_bp_name, agent_hs_name, agent_sp_name]
            for i, result_or_exc in enumerate(stage2_results_list):
                agent_name = parallel_agent_names[i]
                agent_key = agent_names_map[agent_name]

                if isinstance(result_or_exc, Exception):
                    print(f"Exception in parallel agent {agent_name}: {str(result_or_exc)}")
                    results[agent_name] = {"status": "error", "error": str(result_or_exc), "agent_type": agent_name}
                    self._update_session_completion("failed")
                    raise HTTPException(status_code=500, detail=f"Error in {agent_name} (parallel stage): {str(result_or_exc)}")
                
                result = result_or_exc
                if result.get("status") == "error":
                    print(f"Error in parallel agent {agent_name}: {result.get('error', 'Unknown error')}")
                    results[agent_name] = result
                    self._update_session_completion("failed")
                    raise HTTPException(status_code=500, detail=f"Error in {agent_name} (parallel stage): {result.get('error', 'Unknown error')}")

                results[agent_name] = result
                cumulative_input_data[agent_key] = result

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
            bc_result = await self.rate_limited_process(agent_bc, cumulative_input_data.copy(), agent_bc_name)
            if bc_result.get("status") == "error":
                print(f"Error in {agent_bc_name}: {bc_result.get('error', 'Unknown error')}")
                results[agent_bc_name] = bc_result
                self._update_session_completion("failed")
                raise HTTPException(status_code=500, detail=f"Error in {agent_bc_name}: {bc_result.get('error', 'Unknown error')}")
            results[agent_bc_name] = bc_result

            # Update session status to completed
            self._update_session_completion("completed")

        except HTTPException as he:
            print(f"Orchestrator caught HTTPException: {he.detail}")
            # Ensure a consistent error structure if an agent fails mid-process
            # The 'results' dictionary might be partially filled.
            # The HTTPException will be propagated up by FastAPI.
            # We could add more details to the 'results' if needed here.
            
            # Log the error to database
            if self.db_enabled and self.current_session_id and DATABASE_AVAILABLE:
                try:
                    DatabaseService.log_system_event(
                        log_level="ERROR",
                        component="orchestrator",
                        message=f"Analysis session {self.current_session_id} failed: {he.detail}",
                        session_id=self.current_session_id,
                        details={"error": he.detail, "status_code": he.status_code}
                    )
                except Exception as e:
                    print(f"Failed to log error to database: {e}")
            
            return {
                "status": "error",
                "error_detail": he.detail,
                "completed_stages_results": results, # Return what was completed
                "session_id": self.current_session_id  # Include session ID for reference
            }
        except Exception as e:
            print(f"Unexpected error in OrchestratorAgent.process: {str(e)}")
            
            # Update session status to failed and log error
            self._update_session_completion("failed")
            if self.db_enabled and self.current_session_id and DATABASE_AVAILABLE:
                try:
                    DatabaseService.log_system_event(
                        log_level="ERROR",
                        component="orchestrator",
                        message=f"Analysis session {self.current_session_id} failed unexpectedly: {str(e)}",
                        session_id=self.current_session_id,
                        details={"error": str(e)}
                    )
                except Exception as db_e:
                    print(f"Failed to log error to database: {db_e}")
            
            return {
                "status": "error",
                "error_detail": f"Orchestrator failed: {str(e)}",
                "completed_stages_results": results,
                "session_id": self.current_session_id
            } 
            
        # Add session ID to successful results
        if self.current_session_id:
            results["session_id"] = self.current_session_id
            
        return results 